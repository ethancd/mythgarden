from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Hero(models.Model):
    name = models.CharField(max_length=255)
    portrait = models.ImageField(upload_to='portraits/', null=True, blank=True)

    def __str__(self):
        return self.name


class Rucksack(models.Model):
    hero = models.OneToOneField(Hero, on_delete=models.CASCADE, primary_key=True)
    contents = models.ManyToManyField('Item', null=True, blank=True)

    def __str__(self):
        return self.contents


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
    days = models.CharField(max_length=1, choices=DAYS_OF_WEEK)
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

    def __str__(self):
        return self.name


class Building(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='buildings/', null=True, blank=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='items/', null=True, blank=True)

    def __str__(self):
        return self.name


class Villager(models.Model):
    name = models.CharField(max_length=255)
    portrait = models.ImageField(upload_to='portraits/', null=True, blank=True)
    home = models.ForeignKey(Building, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

DIRECTIONS = [
    (0, 'North'),
    (1, 'East'),
    (2, 'South'),
    (3, 'West'),
]

class Action(models.Model):
    ACTION_TYPES = [
        (0, 'Travel'),
        (1, 'Talk'),
        (2, 'Plant'),
        (3, 'Water'),
        (4, 'Harvest'),
        (5, 'Buy'),
        (6, 'Sell'),
    ]

    COST_UNITS = [
        (0, 'm'),
        (1, 'h'),
        (2, 'd'),
        (3, '₭'),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target_object = GenericForeignKey('content_type', 'object_id')  # this can be an Item or a Villager

    description = models.CharField(max_length=255)

    cost_amount = models.IntegerField(default=0)
    cost_unit = models.CharField(max_length=1, choices=COST_UNITS)

    action_type = models.CharField(max_length=1, choices=ACTION_TYPES)
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
        return self.place_1 + ' on the ' + self.get_place_1_relative_direction_display() + ' is adjacent to ' + self.place_2 + ' to the ' + self.get_place_2_relative_direction_display()


class Situation(models.Model):
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)

    contents = models.ManyToManyField('Item', null=True, blank=True)
    occupants = models.ManyToManyField('Villager', null=True, blank=True)

    def __str__(self):
        return self.hero + ' in ' + self.place
