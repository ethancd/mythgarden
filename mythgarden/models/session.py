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

    @property
    def location_state(self):
        # session.place_states.place is prefetched
        for place_state in self.place_states.all():
            if place_state.place.name == self.location.name:
                # don't worry, place names are unique.
                # just matching by name so we don't have to grab the place object for self.location if it's a building
                return place_state

    def get_place_state(self, place):
        if not place:
            return None

        return self.place_states.get(place=place)

    @property
    def occupant_states(self):
        return self.location_state.occupants.all()

    def get_villager_state(self, villager):
        # session.villager_states.villager is prefetched
        if not villager:
            return None

        for villager_state in self.villager_states.all():
            if villager_state.villager == villager:
                return villager_state

    @property
    def local_item_tokens(self):
        return self.location_state.item_tokens.all()

    @property
    def event_states(self):
        return self.scheduled_event_states.all()

    @property
    def high_score(self):
        return self.hero.high_score

    @property
    def boost_level(self):
        return self.hero.boost_level

    @property
    def hero_name(self):
        return self.hero.name

    def reset_session_state(self, end_of_game_message):
        key = self.key
        hero = self.hero

        self.delete()

        return Session.objects.create(key=key, hero=hero, initial_message_text=end_of_game_message)

    def abbr_key_tag(self):
        return f'({self.key[:8]}...)'

    def __str__(self):
        return 'Session ' + self.abbr_key_tag()
