from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver


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
        return str(self.contents)


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
    day = models.CharField(max_length=9, choices=DAYS_OF_WEEK)
    time = models.FloatField(default=0)

    def __str__(self):
        return self.get_day_display() + ' ' + str(self.time)


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
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, default=Place.get_default_pk)

    contents = models.ManyToManyField('Item', blank=True)
    occupants = models.ManyToManyField('Villager', blank=True)

    def __str__(self):
        return self.hero + ' in ' + self.place


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

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
