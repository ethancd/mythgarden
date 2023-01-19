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
    DAYS_OF_WEEK = [
        (0, 'Sun'),
        (1, 'Mon'),
        (2, 'Tue'),
        (3, 'Wed'),
        (4, 'Thu'),
        (5, 'Fri'),
        (6, 'Sat'),
    ]

    hero = models.OneToOneField(Hero, on_delete=models.CASCADE, primary_key=True)
    day = models.IntegerField(choices=DAYS_OF_WEEK)
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
    LANDMARK_TYPES = [
        (0, 'Field'),
        (1, 'Shop'),
        (2, 'House'),
    ]

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='landmarks/', null=True, blank=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='landmarks')
    landmark_type = models.IntegerField(choices=LANDMARK_TYPES, null=True, blank=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    SEED = 'SEED'
    SHOOT = 'SHOOT'
    CROP = 'CROP'
    GIFT = 'GIFT'

    ITEM_TYPES = [
        (SEED, 'Seed'),
        (SHOOT, 'Shoot'),
        (CROP, 'Crop'),
        (GIFT, 'Gift'),
    ]

    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='items/', null=True, blank=True)
    item_type = models.IntegerField(choices=ITEM_TYPES, null=True, blank=True)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Villager(models.Model):
    name = models.CharField(max_length=255)
    portrait = models.ImageField(upload_to='portraits/', null=True, blank=True)
    home = models.ForeignKey(Landmark, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


DIRECTIONS = [
    (0, 'North'),
    (1, 'East'),
    (2, 'South'),
    (3, 'West'),
]


class Action(models.Model):
    TRA = 'TRAVEL'
    TAL = 'TALK'
    GIF = 'GIFT'
    WAT = 'WATER'
    PLA = 'PLANT'
    HAR = 'HARVEST'
    BUY = 'BUY'
    SEL = 'SELL'

    ACTION_TYPES = [
        (TRA, 'Travel'),
        (TAL, 'Talk'),
        (GIF, 'Gift'),
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

    cost_amount = models.IntegerField(default=0)
    cost_unit = models.CharField(max_length=6, choices=COST_UNITS)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target_object = GenericForeignKey('content_type', 'object_id')  # this can be an Item or a Villager
    secondary_target_object = GenericForeignKey('content_type', 'object_id')  # for when an action requires two objects
    direction = models.CharField(max_length=1, choices=DIRECTIONS, null=True, blank=True)

    log_statement = models.CharField(max_length=255)  # this should really be generated from the action_type

    def __str__(self):
        return self.description

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class Bridge(models.Model):
    place_1 = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='place_1')
    place_2 = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='place_2')

    place_1_relative_direction = models.CharField(max_length=1, choices=DIRECTIONS)
    place_2_relative_direction = models.CharField(max_length=1, choices=DIRECTIONS)

    def __str__(self):
        return str(self.place_1) + ' on the ' + self.get_place_1_relative_direction_display() + ' is adjacent to ' + str(self.place_2) + ' to the ' + self.get_place_2_relative_direction_display()


class Situation(models.Model):
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, default=Place.get_default_pk)

    contents = models.ManyToManyField('Item', blank=True)
    occupants = models.ManyToManyField('Villager', blank=True)

    def __str__(self):
        return self.hero + ' in ' + self.place


