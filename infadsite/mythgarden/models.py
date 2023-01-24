from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError


class Hero(models.Model):
    name = models.CharField(max_length=255)
    portrait = models.ImageField(upload_to='portraits/', null=True, blank=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=Hero)
def create_belongings(sender, instance, created, **kwargs):
    if created:
        Rucksack.objects.create(hero=instance)
        Clock.objects.create(hero=instance)
        Wallet.objects.create(hero=instance)
        Situation.objects.create(hero=instance)


class Rucksack(models.Model):
    hero = models.OneToOneField(Hero, on_delete=models.CASCADE, primary_key=True)
    contents = models.ManyToManyField('Item', blank=True)

    def __str__(self):
        return str(self.hero) + "'s rucksack"


class Clock(models.Model):
    SUNDAY = 'SUN'
    MONDAY = 'MON'
    TUESDAY = 'TUE'
    WEDNESDAY = 'WED'
    THURSDAY = 'THU'
    FRIDAY = 'FRI'
    SATURDAY = 'SAT'

    DAYS_OF_WEEK = [
        (SUNDAY, 'Sun'),
        (MONDAY, 'Mon'),
        (TUESDAY, 'Tue'),
        (WEDNESDAY, 'Wed'),
        (THURSDAY, 'Thu'),
        (FRIDAY, 'Fri'),
        (SATURDAY, 'Sat'),
    ]

    hero = models.OneToOneField(Hero, on_delete=models.CASCADE, primary_key=True)
    day = models.CharField(default=SUNDAY, max_length=9, choices=DAYS_OF_WEEK)
    time = models.FloatField(default=0, validators=[MinValueValidator(0.0), MaxValueValidator(24.0)])

    def __str__(self):
        return self.get_day_display() + ' ' + self.get_time_display()

    def get_time_display(self):
        hours = int(self.time) % 12
        if hours == 0:
            hours = 12
        minutes = int((self.time - int(self.time)) * 60)
        suffix = 'pm' if self.time >= 12 else 'am'

        return f"{hours}:{minutes:02d}{suffix}"

    def advance(self, duration, unit):
        """ Updates the day and time by the given amount of time,
        rolling the clock and days over at midnight and end of saturday respectively. """

        amount_in_hours = self.parse_duration(duration, unit)
        self.time += amount_in_hours

        if self.time >= 24:
            days_to_add = int(self.time / 24)
            self.time = self.time % 24
            self.advance_day(days_to_add)

    # noinspection PyMethodMayBeStatic
    def parse_duration(self, duration, unit):
        if unit == Action.HOUR:
            return float(duration)
        elif unit == Action.MIN:
            return float(duration / 60)
        elif unit == Action.DAY:
            return float(duration * 24)
        else:
            raise ValueError(f"Invalid duration unit: {unit}")

    def advance_day(self, days_to_add):
        """ Advances the day by the given number of days, rolling over at the end of the week. """
        current_day_index = self.DAYS_OF_WEEK.index((self.day, self.get_day_display()))
        new_day_index = (current_day_index + days_to_add) % 7
        self.day = self.DAYS_OF_WEEK[new_day_index][0]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Wallet(models.Model):
    hero = models.OneToOneField(Hero, on_delete=models.CASCADE, primary_key=True)
    money = models.IntegerField(default=0)

    def __str__(self):
        return str(self.money)


class Place(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='places/', null=True, blank=True)

    @classmethod
    def get_default_pk(cls):
        place, created = cls.objects.get_or_create(name='The Farm')
        return place.pk

    def __str__(self):
        return self.name


class Landmark(models.Model):
    FIELD = 'FIELD'
    SHOP = 'SHOP'
    HOUSE = 'HOUSE'

    LANDMARK_TYPES = [
        (FIELD, 'Field'),
        (SHOP, 'Shop'),
        (HOUSE, 'House'),
    ]

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='landmarks/', null=True, blank=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='landmarks')
    landmark_type = models.CharField(max_length=5, choices=LANDMARK_TYPES, default=HOUSE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.guard_landmark_constraints_on_place(self.place, self.landmark_type)
        return super().save(*args, **kwargs)

    # noinspection PyMethodMayBeStatic
    def guard_landmark_constraints_on_place(self, place, landmark_type):
        """ Ensures that only one of {field or shop} exists per place. """
        landmark_is_field_or_shop = landmark_type in [Landmark.FIELD, Landmark.SHOP]
        place_has_field_or_shop = place.landmarks.filter(landmark_type__in=[Landmark.FIELD, Landmark.SHOP]).exists()

        if landmark_is_field_or_shop and place_has_field_or_shop:
            raise ValidationError('A place can only have one of: field, shop.')


class Item(models.Model):
    SEED = 'SEED'
    SPROUT = 'SPROUT'
    CROP = 'CROP'
    GIFT = 'GIFT'

    ITEM_TYPES = [
        (SEED, 'Seed'),
        (SPROUT, 'Sprout'),
        (CROP, 'Crop'),
        (GIFT, 'Gift'),
    ]

    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='items/', null=True, blank=True)
    item_type = models.CharField(max_length=6, choices=ITEM_TYPES, default=GIFT)
    price = models.IntegerField(default=1)

    def __str__(self):
        return self.name


class Villager(models.Model):
    name = models.CharField(max_length=255)
    portrait = models.ImageField(upload_to='portraits/', null=True, blank=True)
    home = models.ForeignKey(Landmark, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Bridge(models.Model):
    NORTH = 'NORTH'
    EAST = 'EAST'
    SOUTH = 'SOUTH'
    WEST = 'WEST'

    DIRECTIONS = [
        (NORTH, 'North'),
        (EAST, 'East'),
        (SOUTH, 'South'),
        (WEST, 'West'),
    ]

    place_1 = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='place_1')
    place_2 = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='place_2')

    direction_1 = models.CharField(max_length=5, choices=DIRECTIONS)
    direction_2 = models.CharField(max_length=5, choices=DIRECTIONS)

    def __str__(self):
        return str(self.place_1) + ' on the ' + self.get_direction_1_display() + ' is adjacent to ' + str(
            self.place_2) + ' to the ' + self.get_direction_2_display()


class Situation(models.Model):
    hero = models.OneToOneField(Hero, on_delete=models.CASCADE, related_name='situation')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, default=Place.get_default_pk)

    contents = models.ManyToManyField('Item', blank=True)
    occupants = models.ManyToManyField('Villager', blank=True)

    def __str__(self):
        return str(self.hero) + ' in ' + str(self.place)


class Action(models.Model):
    TRA = 'TRAVEL'
    TAL = 'TALK'
    GIV = 'GIVE'
    WAT = 'WATER'
    PLA = 'PLANT'
    HAR = 'HARVEST'
    BUY = 'BUY'
    SEL = 'SELL'

    ACTION_TYPES = [
        (TRA, 'Travel'),
        (TAL, 'Talk'),
        (GIV, 'Give'),
        (PLA, 'Plant'),
        (WAT, 'Water'),
        (HAR, 'Harvest'),
        (BUY, 'Buy'),
        (SEL, 'Sell'),
    ]

    MIN = 'MINUTE'
    HOUR = 'HOUR'
    DAY = 'DAY'
    KOIN = 'KOIN'

    COST_UNITS = [
        (MIN, 'm'),
        (HOUR, 'h'),
        (DAY, 'd'),
        (KOIN, '₭'),
    ]

    TIME_UNITS = [MIN, HOUR, DAY]
    MONEY_UNITS = [KOIN]

    action_type = models.CharField(max_length=7, choices=ACTION_TYPES)
    description = models.CharField(max_length=255)

    cost_amount = models.IntegerField(default=1)
    cost_unit = models.CharField(max_length=6, choices=COST_UNITS)

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target_object = GenericForeignKey('content_type', 'object_id')  # this can be an Item or a Villager

    secondary_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True,
                                               related_name='secondary_content_type')
    secondary_object_id = models.PositiveIntegerField(null=True, blank=True)
    secondary_target_object = GenericForeignKey('secondary_content_type',
                                                'secondary_object_id')  # for when an action requires two objects

    direction = models.CharField(max_length=5, choices=Bridge.DIRECTIONS, null=True, blank=True)

    log_statement = models.CharField(
        max_length=255)  # this should really be generated from the action_type, direct objects, etc

    def __str__(self):
        return self.description

    @property
    def display_cost(self):
        if self.is_cost_in_money():
            return self.get_cost_unit_display() + str(self.cost_amount)
        else:
            return str(self.cost_amount) + self.get_cost_unit_display()

    def is_cost_in_money(self):
        return self.cost_unit in self.MONEY_UNITS

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
