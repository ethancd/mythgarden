from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from ._constants import MINUTES_IN_A_DAY, DAYS_OF_WEEK, SUNDAY, DAWN, MINUTES_IN_A_HALF_DAY, \
    OVERSLEPT_TIME, DAY_TO_INDEX


class Clock(models.Model):
    session = models.OneToOneField('Session', on_delete=models.CASCADE, primary_key=True)
    day = models.CharField(default=SUNDAY, max_length=9, choices=DAYS_OF_WEEK)
    time = models.IntegerField(default=DAWN, validators=[MinValueValidator(0), MaxValueValidator(MINUTES_IN_A_DAY - 1)])
    is_new_day = models.BooleanField(default=False)

    def __str__(self):
        return 'Clock ' + self.session.abbr_key_tag()

    def serialize(self):
        return {
            'display': self.display,
            'time': self.time,
            'day_number': self.day_index
        }

    @property
    def display(self):
        return self.get_day_display() + ' ' + self.get_time_display()

    @property
    def day_index(self):
        return DAY_TO_INDEX[self.day]

    def get_time_display(self):
        """ Returns the time as a string in the format 'hh:mmam' or 'hh:mmpm' """
        hours = (self.time % MINUTES_IN_A_HALF_DAY) // 60
        if hours == 0:
            hours = 12
        minutes = self.time % 60
        suffix = 'pm' if self.time >= MINUTES_IN_A_HALF_DAY else 'am'

        return f"{hours}:{minutes:02d}{suffix}"

    def advance(self, amount_in_minutes):
        """ Updates the day and time by the given amount of time,
        rolling the clock and days over at midnight and end of saturday respectively. """

        self.time += amount_in_minutes

        days_to_add = self.time // MINUTES_IN_A_DAY
        if days_to_add > 0:
            self.time = self.time % MINUTES_IN_A_DAY
            self.advance_day(days_to_add)

    def advance_day(self, days_to_add):
        """ Advances the day by the given number of days, rolling over at the end of the week. """
        new_day_index = (self.day_index + days_to_add) % 7
        self.day = DAYS_OF_WEEK[new_day_index][0]
        self.is_new_day = True

    def is_now(self, day, time):
        return self.day == day and self.time == time

    def is_in_past(self, day, time):
        is_past_day = DAY_TO_INDEX[self.day] > DAY_TO_INDEX[day]
        return is_past_day or (self.day == day and self.time > time)

    def is_now_or_in_past(self, day, time):
        return self.is_now(day, time) or self.is_in_past(day, time)

    @property
    def minutes_to_midnight(self):
        return MINUTES_IN_A_DAY - self.time

    @property
    def minutes_to_dawn(self):
        return DAWN - self.time

    @property
    def minutes_to_overslept_time(self):
        return OVERSLEPT_TIME - self.time

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
