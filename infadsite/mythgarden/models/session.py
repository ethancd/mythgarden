from django.db import models

from .event import ScheduledEvent, ScheduledEventState
from .hero import Hero
from .place import Place
from .villager import VillagerState
from ..static_helpers import generate_uuid

from ._constants import WELCOME_MESSAGE


class Session(models.Model):
    key = models.CharField(max_length=32, primary_key=True, default=generate_uuid)
    location = models.ForeignKey(Place, on_delete=models.CASCADE, null=True, default=Place.get_default_pk)
    hero = models.ForeignKey('Hero', on_delete=models.CASCADE, related_name='current_session', null=True, default=Hero.get_default_pk)

    is_first_session = models.BooleanField(default=False)
    skip_post_save_signal = models.BooleanField(default=False)
    initial_message_text = models.CharField(max_length=255, default=WELCOME_MESSAGE)
    game_over = models.BooleanField(default=False)

    def save_data(self):
        """save model objects that the current session has a handle on –
        so excluding place_states and villager_states"""

        self.save()
        self.hero_state.save()
        self.wallet.save()
        self.inventory.save()  # probably unnecessary, since inventory doesn't have any fields right now
        self.clock.save()

    @property
    def location_state(self):
        return self.place_states.get(place=self.location)

    def get_place_state(self, place):
        if not place:
            return None

        return self.place_states.get(place=place)

    @property
    def occupant_states(self):
        return self.location_state.occupants.all()

    def get_villager_state(self, villager):
        if not villager:
            return None

        return self.villager_states.get(villager=villager)

    @property
    def local_item_tokens(self):
        return self.location_state.item_tokens.all()

    @property
    def event_states(self):
        return self.scheduled_event_states.all()

    def reset_session_state(self, end_of_game_message):
        key = self.key
        hero = self.hero

        self.delete()

        return Session.objects.create(key=key, hero=hero, initial_message_text=end_of_game_message)

    def abbr_key_tag(self):
        return f'({self.key[:8]}...)'

    def __str__(self):
        return 'Session ' + self.abbr_key_tag()
