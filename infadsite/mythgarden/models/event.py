from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from ._constants import DAYS_OF_WEEK, MINUTES_IN_A_DAY, DAWN, SUNDAY


class ScheduledEvent(models.Model):
    ITEMS_APPEAR = 'ITEMS_APPEAR'

    EVENT_TYPES = [
        (ITEMS_APPEAR, 'Items appear'),
    ]

    day = models.CharField(default=SUNDAY, max_length=9, choices=DAYS_OF_WEEK)
    time = models.IntegerField(default=DAWN,
                               validators=[MinValueValidator(0), MaxValueValidator(MINUTES_IN_A_DAY - 1)])

    place = models.ForeignKey('Place', on_delete=models.SET_NULL, null=True, blank=True, related_name='scheduled_events')
    items = models.ManyToManyField('Item', blank=True, related_name='scheduled_events')

    event_type = models.CharField(max_length=12, choices=EVENT_TYPES, default=ITEMS_APPEAR)

    def __str__(self):
        return f'Scheduled Event: {self.get_event_type_display()} in {self.place} at {self.time} on {self.day}'


class ScheduledEventState(models.Model):
    event = models.ForeignKey('ScheduledEvent', on_delete=models.CASCADE, related_name='states')
    session = models.ForeignKey('Session', on_delete=models.CASCADE, related_name='scheduled_event_states')
    has_occurred = models.BooleanField(default=False)

    def __str__(self):
        return str(self.event) + ' ' + self.session.abbr_key_tag()

    def mark_as_occurred(self):
        self.has_occurred = True
        self.save()
