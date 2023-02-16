from django.db import models

from .event import ScheduledEvent, ScheduledEventState
from .place import Place
from .villager import VillagerState
from ..static_helpers import generate_uuid


class Session(models.Model):
    key = models.CharField(max_length=32, primary_key=True, default=generate_uuid)
    location = models.ForeignKey(Place, on_delete=models.CASCADE, null=True, default=Place.get_default_pk)
    skip_post_save_signal = models.BooleanField(default=False)
    message = models.TextField(blank=True, null=True)
    game_over = models.BooleanField(default=False)

    def save_data(self):
        """save model objects that the current session has a handle on --
        so excluding place_states and villager_states"""

        self.save()
        self.hero.save()
        self.wallet.save()
        self.inventory.save()  # probably unnecessary, since inventory doesn't have any fields right now
        self.clock.save()

    @property
    def location_state(self):
        return self.place_states.get_or_create(place=self.location)[0]

    @property
    def occupants(self):
        return self.location_state.occupants.all()

    @property
    def occupant_states(self):
        occupant_states = self.villager_states.filter(villager__in=self.occupants)

        # ensure all occupants have a state
        for villager in self.occupants.all():
            if occupant_states.filter(villager=villager).exists():
                continue

            villager_state = self.villager_states.create(villager=villager, location=self.location)
            occupant_states |= VillagerState.objects.filter(pk=villager_state.pk)

        return occupant_states

    def get_villager_state(self, villager):
        return self.occupant_states.filter(villager=villager).first()

    @property
    def local_item_tokens(self):
        return self.location_state.item_tokens.all()

    @property
    def event_states(self):
        event_states = self.scheduled_event_states.all()

        # ensure all events have a state
        for event in ScheduledEvent.objects.all():
            if event_states.filter(event=event).exists():
                continue

            event_state = self.scheduled_event_states.create(event=event)
            event_states |= ScheduledEventState.objects.filter(pk=event_state.pk)

        return event_states

    def reset_session_state(self, end_of_game_message=None):
        key = self.key

        self.delete()

        return Session.objects.create(key=key, message=end_of_game_message)

    def abbr_key_tag(self):
        return f'({self.key[:8]}...)'

    def __str__(self):
        return 'Session ' + self.abbr_key_tag()
