from django.db import models

from .event import ScheduledEvent, ScheduledEventState
from .item import ItemToken
from .place import Place
from .villager import VillagerState
from ._constants import FARM, SEED, SPROUT
from mythgarden.static_helpers import generate_uuid


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

    def trigger_scheduled_events(self):
        """Check if the time for any scheduled events has come (or just passed)"""
        for event_state in self.event_states.filter(has_occurred=False):
            event = event_state.event

            if self.clock.is_now_or_in_past(event.day, event.time):
                self.trigger_event(event)
                event_state.has_occurred = True
                event_state.save()

    def trigger_event(self, event):
        """Trigger an event based on the event_type"""
        if event.event_type == ScheduledEvent.ITEMS_APPEAR:
            self.make_items_appear(event)

    def make_items_appear(self, event):
        """Make items appear in the place saved on the event"""
        item_tokens = []
        for item in event.items.all():
            item_tokens.append(ItemToken(session=self, item=item))
        ItemToken.objects.bulk_create(item_tokens)

        place_state, created = self.place_states.get_or_create(place=event.place)

        place_state.item_tokens.set(item_tokens)

    def reset_for_new_day(self):
        self.reset_villager_states()
        self.grow_crops()

    def reset_villager_states(self):
        self.villager_states.all().update(has_been_talked_to=False, has_been_given_gift=False)

    def grow_crops(self):
        """Find all seeds/sprouts in the farm and "grow" them if they've been watered --
        ie replace them with a new item token at the next growth stage."""
        farm_state = self.place_states.get(place__place_type=FARM)
        item_tokens = farm_state.item_tokens.all()
        new_contents = []

        for token in item_tokens:
            if token.item_type not in [SEED, SPROUT]:
                new_contents.append(token)
                continue

            if not token.has_been_watered:
                new_contents.append(token)
                continue

            new_item = token.item.get_next_growth_stage()
            new_item_token = ItemToken.objects.create(session=self, item=new_item)
            new_contents.append(new_item_token)

        farm_state.item_tokens.set(new_contents)

    def trigger_game_over(self):
        koin = self.hero.koin_earned
        hearts = self.hero.hearts_earned
        score = self.hero.score

        new_session = self.reset_session_state()

        # new_session.new_game = True
        new_session.message = f'You made it to the end of the week! You earned {koin} koin and {hearts} hearts, for a total score of {score}.'\
        'Prepare to enter the time loop and start over again!'

        new_session.save()

    def reset_session_state(self):
        key = self.key

        self.delete()

        return Session.objects.create(key=key)

    def abbr_key_tag(self):
        return f'({self.key[:8]}...)'

    def __str__(self):
        return 'Session ' + self.abbr_key_tag()
