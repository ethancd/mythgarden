from django.core.validators import ValidationError
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from .models._constants import MAX_ITEMS, SHOP
from .models.clock import Clock
from .models.hero import Hero, HeroState
from .models.game_settings import GameSettings
from .models.inventory import Inventory
from .models.item import Item, ItemToken
from .models.message import Message
from .models.place import Place, PlaceState
from .models.session import Session
from .models.villager import Villager, VillagerState
from .models.wallet import Wallet


@receiver(m2m_changed, sender=Inventory.item_tokens.through)
def inventory_items_changed(sender, instance, action, **kwargs):
    if action == 'post_add' and instance.item_tokens.count() > MAX_ITEMS:
        raise ValidationError(f'⚠️ Inventory cannot hold more than {MAX_ITEMS} items.')


@receiver(m2m_changed, sender=PlaceState.item_tokens.through)
def local_items_changed(sender, instance, action, **kwargs):
    if action == 'post_add' and instance.item_tokens.count() > MAX_ITEMS:
        raise ValidationError(f'⚠️ {instance.place.name} cannot hold more than {MAX_ITEMS} items.')


@receiver(post_save, sender=Session)
def create_session_state(sender, instance, created, **kwargs):
    if created and not instance.skip_post_save_signal:
        # Apply draft settings for new run
        game_settings, _ = GameSettings.objects.get_or_create(hero=instance.hero)
        game_settings.apply_draft()

        HeroState.objects.create(session=instance, hero=instance.hero)
        Inventory.objects.create(session=instance)
        Clock.objects.create(session=instance)
        Wallet.objects.create(session=instance)
        Message.objects.create(session=instance, text=instance.initial_message_text)

        place_state_objects = instance.populate_place_states()
        instance.populate_villager_states(place_state_objects)

        # If using fixed shop mode, populate initial shop inventory
        if not game_settings.dynamic_shop:
            _populate_initial_shop(instance, game_settings, place_state_objects)


def _populate_initial_shop(session, game_settings, place_states):
    """Populate shop with initial inventory when dynamic_shop is disabled."""
    # Find the shop place state
    shop_state = None
    for state in place_states:
        if state.place.place_type == SHOP:
            shop_state = state
            break

    if not shop_state:
        return

    # Determine which seeds to stock based on advanced_crops setting
    if game_settings.advanced_crops:
        seed_names = [
            'Weedbulb Seed',
            'Cool Lettuce Seed',
            'Spice Carrot Seed',
            'Earth Yam Seed',
            'Lightning Artichoke Seed',
            'Hallowed Pumpkin Seed',
            'Mythfruit™ Seed',
        ]
    else:
        seed_names = [
            'Parsnip Seed',
            'Potato Seed',
            'Rhubarb Seed',
            'Cauliflower Seed',
            'Melon Seed',
            'Pumpkin Seed',
            'Mythfruit Seed',
        ]

    # Create item tokens for all seeds (unlimited quantity = None)
    item_tokens = []
    for seed_name in seed_names:
        try:
            item = Item.objects.get(name=seed_name)
            item_token = ItemToken.objects.create(session=session, item=item, quantity=None)
            item_tokens.append(item_token)
        except Item.DoesNotExist:
            # Skip if seed doesn't exist yet (might not have run migration)
            pass

    # Set the shop inventory
    if item_tokens:
        shop_state.item_tokens.set(item_tokens)


@receiver(post_save, sender=Hero)
def create_game_settings(sender, instance, created, **kwargs):
    if created:
        GameSettings.objects.create(hero=instance)
