from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from ._constants import DAYS_OF_WEEK, MINUTES_IN_A_DAY, DAWN

from .place import Place


class ScheduledEvent(models.Model):
    SHOP_POPULATES = 'SHOP_POPULATES'
    VILLAGER_APPEARS = 'VILLAGER_APPEARS'

    EVENT_TYPES = [
        (SHOP_POPULATES, 'Shop populates'),
        (VILLAGER_APPEARS, 'Villager appears'),
    ]

    day = models.CharField(max_length=9, choices=DAYS_OF_WEEK, null=True)
    is_daily = models.BooleanField(default=False)
    time = models.IntegerField(default=DAWN,
                               validators=[MinValueValidator(0), MaxValueValidator(MINUTES_IN_A_DAY - 1)])

    event_type = models.CharField(max_length=16, choices=EVENT_TYPES)

    def __str__(self):
        return f'Scheduled Event: {self.get_event_type_display()} at {self.time} on {self.day}'


class PopulateShopEvent(ScheduledEvent):
    shop = models.ForeignKey('Place', on_delete=models.CASCADE, default=Place.get_default_shop_pk)
    content_config_list = models.JSONField(default=list)

    def save(self, *args, **kwargs):
        if not self.event_type:
            self.event_type = ScheduledEvent.SHOP_POPULATES

        return super().save(*args, **kwargs)


class VillagerAppearsEvent(ScheduledEvent):
    place = models.ForeignKey('Place', on_delete=models.CASCADE, null=True, blank=True)
    villager = models.ForeignKey('Villager', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.event_type:
            self.event_type = ScheduledEvent.VILLAGER_APPEARS

        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Event: {self.villager} appears in {self.place} at {self.time} on {self.day}'


class ScheduledEventState(models.Model):
    event = models.ForeignKey('ScheduledEvent', on_delete=models.CASCADE, related_name='states')
    session = models.ForeignKey('Session', on_delete=models.CASCADE, related_name='scheduled_event_states')
    has_occurred = models.BooleanField(default=False)

    def __str__(self):
        return str(self.event) + ' ' + self.session.abbr_key_tag()
