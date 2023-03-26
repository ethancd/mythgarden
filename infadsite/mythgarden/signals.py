from django.core.validators import ValidationError
from django.db import transaction
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from .game_logic import EventOperator
from .models._constants import MAX_ITEMS
from .models.clock import Clock
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

        for place in list(Place.objects.all()):
            PlaceState.objects.create(session=instance, place=place)

        for villager in list(Villager.objects.all()):
            VillagerState.objects.create(session=instance, villager=villager)

