from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError

from .static_helpers import generate_uuid


class Inventory(models.Model):
    session = models.OneToOneField('Session', on_delete=models.CASCADE, primary_key=True)
    items = models.ManyToManyField('Item', blank=True)

    def __str__(self):
        return 'Inventory ' + self.session.abbr_key_tag()


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

    session = models.OneToOneField('Session', on_delete=models.CASCADE, primary_key=True)
    day = models.CharField(default=SUNDAY, max_length=9, choices=DAYS_OF_WEEK)
    time = models.FloatField(default=0, validators=[MinValueValidator(0.0), MaxValueValidator(24.0)])

    def __str__(self):
        return 'Clock ' + self.session.abbr_key_tag()

    def serialize(self):
        return self.display

    @property
    def display(self):
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
    session = models.OneToOneField('Session', on_delete=models.CASCADE, primary_key=True)
    money = models.IntegerField(default=0)

    def __str__(self):
        return 'Wallet ' + self.session.abbr_key_tag()

    def serialize(self):
        return self.display

    @property
    def display(self):
        return Action.KOIN_SIGN + str(self.money)


class PlaceManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Place(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='places/', default='places/idyllic-green-farm.png')

    FARM = 'FARM'
    TOWN = 'TOWN'
    MOUNTAIN = 'MOUNTAIN'
    FOREST = 'FOREST'
    BEACH = 'BEACH'
    SHOP = 'SHOP'
    HOME = 'HOME'

    WILD_TYPES = ['MOUNTAIN', 'FOREST', 'BEACH']

    PLACE_TYPES = [
        (FARM, 'Farm'),
        (MOUNTAIN, 'Mountain'),
        (FOREST, 'Forest'),
        (BEACH, 'Beach'),
        (TOWN, 'Town'),
        (SHOP, 'Shop'),
        (HOME, 'Home'),
    ]

    place_type = models.CharField(max_length=8, choices=PLACE_TYPES, default=TOWN)

    default_contents = models.ManyToManyField('Item', blank=True)

    item_pool = models.ManyToManyField('Item', blank=True, related_name='pool_locations')

    objects = PlaceManager()

    @classmethod
    def get_default_pk(cls):
        place, created = cls.objects.get_or_create(name='The Farm')
        return place.pk

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            'name': self.name,
            'image': {
                'url': self.image.url if self.image else None
            },
        }


class Building(Place):
    surround = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='buildings')

    def __str__(self):
        return super().__str__()

    def serialize(self):
        return super().serialize()


class PlaceState(models.Model):
    session = models.ForeignKey('Session', on_delete=models.CASCADE, related_name='place_states')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='states')

    contents = models.ManyToManyField('Item', blank=True)
    occupants = models.ManyToManyField('Villager', blank=True)

    def __str__(self):
        return f'{self.place} state ' + self.session.abbr_key_tag()

    def save(self, *args, **kwargs):
        # save place state first so we can have id and assign contents and occupants
        super().save(*args, **kwargs)

        # set contents and occupants based on place defaults

        self.contents.set(self.place.default_contents.all())

        try:
            building = self.place.building
            self.occupants.set(building.residents.all())
        except Building.DoesNotExist:
            pass


class Session(models.Model):
    key = models.CharField(max_length=32, primary_key=True, default=generate_uuid)
    location = models.ForeignKey(Place, on_delete=models.CASCADE, null=True, default=Place.get_default_pk)
    skip_post_save_signal = models.BooleanField(default=False)

    def save_data(self):
        """save objects related to the session, excluding:
        place_session_data for non-current locations,
        villager_session_data for non-present villagers
        """

        self.save()
        self.hero.save()
        self.clock.save()
        self.wallet.save()
        self.inventory.save()
        self.location_state.save()
        [o.save() for o in self.occupant_states]

    @property
    def location_state(self):
        return self.place_states.get_or_create(place=self.location)[0]

    @property
    def occupants(self):
        return self.location_state.occupants.all()

    @property
    def occupant_states(self):
        occupant_states = []
        for villager in self.occupants.all():
            villager_state, created = self.villager_states.get_or_create(villager=villager, location=self.location)
            occupant_states.append(villager_state)

        return occupant_states

    def abbr_key_tag(self):
        return f'({self.key[:8]}...)'

    def __str__(self):
        return 'Session ' + self.abbr_key_tag()


@receiver(post_save, sender=Session)
def create_belongings(sender, instance, created, **kwargs):
    if created and not instance.skip_post_save_signal:
        Hero.objects.create(session=instance)
        Inventory.objects.create(session=instance)
        Clock.objects.create(session=instance)
        Wallet.objects.create(session=instance)


class Hero(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255, default='Squall')
    portrait = models.ImageField(upload_to='portraits/', default='portraits/squall-farmer.png')

    def __str__(self):
        return 'Hero ' + self.session.abbr_key_tag()


class ItemManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


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

    COMMON = 'COMMON'
    UNCOMMON = 'UNCOMMON'
    RARE = 'RARE'
    EPIC = 'EPIC'

    RARITIES = [
        COMMON,
        UNCOMMON,
        RARE,
        EPIC
    ]

    RARITY_CHOICES = [
        (COMMON, 'common'),
        (UNCOMMON, 'uncommon'),
        (RARE, 'rare'),
        (EPIC, 'epic'),
    ]

    RARITY_WEIGHTS = {
        COMMON: 0.65,
        UNCOMMON: 0.25,
        RARE: 0.08,
        EPIC: 0.02,
    }

    name = models.CharField(max_length=255, unique=True)
    icon = models.ImageField(upload_to='items/', null=True, blank=True)
    item_type = models.CharField(max_length=6, choices=ITEM_TYPES, default=GIFT)
    price = models.IntegerField(default=1)
    rarity = models.CharField(max_length=8, choices=RARITY_CHOICES, default=COMMON)

    objects = ItemManager()

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            'name': self.name,
            'icon': {
                'url': self.icon.url if self.icon else None
            }
        }


class Villager(models.Model):
    name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    friendliness = models.IntegerField(default=4, validators=[MinValueValidator(1), MaxValueValidator(7)])
    portrait = models.ImageField(upload_to='portraits/', null=True, blank=True, default='portraits/squall-farmer.png')
    home = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True, related_name='residents')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.name

        return super().save(*args, **kwargs)

    def serialize(self):
        return {
            'name': self.name,
            'portrait': {
                'url': self.portrait.url if self.portrait else None
            }
        }


class VillagerState(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='villager_states')
    villager = models.ForeignKey(Villager, on_delete=models.CASCADE, related_name='states')

    affinity = models.IntegerField(default=0)
    location = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='villagers')  # , default=villager.home)

    def __str__(self):
        return f'{self.villager} state ' + self.session.abbr_key_tag()


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


class Action(models.Model):
    TRA = 'TRAVEL'
    TAL = 'TALK'
    GIV = 'GIVE'
    WAT = 'WATER'
    PLA = 'PLANT'
    HAR = 'HARVEST'
    BUY = 'BUY'
    SEL = 'SELL'
    GAT = 'GATHER'

    ACTION_TYPES = [
        (TRA, 'Travel'),
        (TAL, 'Talk'),
        (GIV, 'Give'),
        (PLA, 'Plant'),
        (WAT, 'Water'),
        (HAR, 'Harvest'),
        (BUY, 'Buy'),
        (SEL, 'Sell'),
        (GAT, 'Gather'),
    ]

    MIN = 'MINUTE'
    HOUR = 'HOUR'
    DAY = 'DAY'
    KOIN = 'KOIN'

    KOIN_SIGN = '₭'

    COST_UNITS = [
        (MIN, 'min'),
        (HOUR, 'hour'),
        (DAY, 'day'),
        (KOIN, KOIN_SIGN),
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

    def serialize(self):
        return {
            'description': self.description,
            'display_cost': self.display_cost,
        }

    @property
    def display_cost(self):
        if self.is_cost_in_money():
            return self.get_cost_unit_display() + str(self.cost_amount)
        else:
            return str(self.cost_amount) + ' ' + self.get_cost_unit_display()

    def is_cost_in_money(self):
        return self.cost_unit in self.MONEY_UNITS

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
