from django.core.validators import ValidationError
from django.db import transaction
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from .game_logic import EventOperator
from .models._constants import MAX_ITEMS
from .models.clock import Clock
from .models.event import ScheduledEvent, ScheduledEventState
from .models.hero import HeroState
from .models.inventory import Inventory
from .models.message import Message
from .models.place import Place, PlaceState
from .models.session import Session
from .models.villager import Villager, VillagerState
from .models.wallet import Wallet


@receiver(m2m_changed, sender=Inventory.item_tokens.through)
def inventory_items_changed(sender, instance, action, **kwargs):
    if action == 'post_add' and instance.item_tokens.count() > MAX_ITEMS:
        raise ValidationError(f'Inventory cannot hold more than {MAX_ITEMS} items.')


@receiver(m2m_changed, sender=PlaceState.item_tokens.through)
def local_items_changed(sender, instance, action, **kwargs):
    if action == 'post_add' and instance.item_tokens.count() > MAX_ITEMS:
        raise ValidationError(f'{instance.place.name} cannot hold more than {MAX_ITEMS} items.')


@receiver(post_save, sender=Clock)
def time_has_passed(sender, instance, created, **kwargs):
    if created:
        return

    with transaction.atomic():
        EventOperator().react_to_time_passing(instance, instance.session)


@receiver(post_save, sender=Session)
def create_session_state(sender, instance, created, **kwargs):
    if created and not instance.skip_post_save_signal:
        HeroState.objects.create(session=instance, hero=instance.hero)
        Inventory.objects.create(session=instance)
        Clock.objects.create(session=instance)
        Wallet.objects.create(session=instance)
        Message.objects.create(session=instance, text=instance.initial_message_text)

        place_states = []
        villager_states = []
        event_states = []

        for place in list(Place.objects.all()):
            place_states.append(PlaceState(session=instance, place=place))

        place_state_objs = PlaceState.objects.bulk_create(place_states)

        place_to_state_dict = {state.place.pk: state for state in place_state_objs}

        for villager in list(Villager.objects.all()):
            if villager.home:
                location_state = place_to_state_dict.get(villager.home.pk, None)
                villager_state = VillagerState(session=instance, villager=villager, location_state=location_state)
            else:
                villager_state = VillagerState(session=instance, villager=villager)

            villager_states.append(villager_state)

        villager_state_objs = VillagerState.objects.bulk_create(villager_states)

        for event in list(ScheduledEvent.objects.all()):
            event_states.append(ScheduledEventState(session=instance, event=event))

        event_state_objs = ScheduledEventState.objects.bulk_create(event_states)


