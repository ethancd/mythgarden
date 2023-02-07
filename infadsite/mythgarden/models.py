from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError

from .static_helpers import generate_uuid


class Inventory(models.Model):
    MAX_ITEMS = 6

    session = models.OneToOneField('Session', on_delete=models.CASCADE, primary_key=True)
    item_tokens = models.ManyToManyField('ItemToken', blank=True)

    def __str__(self):
        return 'Inventory ' + self.session.abbr_key_tag()


@receiver(m2m_changed, sender=Inventory.item_tokens.through)
def inventory_items_changed(sender, instance, action, **kwargs):
    if action == 'post_add' and instance.item_tokens.count() > Inventory.MAX_ITEMS:
        raise ValidationError(f'Inventory cannot hold more than {Inventory.MAX_ITEMS} items.')


class Clock(models.Model):
    MINUTES_IN_A_DAY = 24 * 60
    MINUTES_IN_A_HALF_DAY = 12 * 60
    MINUTES_IN_A_QUARTER_DAY = 6 * 60
    DAWN = MINUTES_IN_A_QUARTER_DAY
    OVERSLEPT_TIME = 10 * 60

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

    DAY_TO_INDEX = {
        SUNDAY: 0,
        MONDAY: 1,
        TUESDAY: 2,
        WEDNESDAY: 3,
        THURSDAY: 4,
        FRIDAY: 5,
        SATURDAY: 6,
    }

    session = models.OneToOneField('Session', on_delete=models.CASCADE, primary_key=True)
    day = models.CharField(default=SUNDAY, max_length=9, choices=DAYS_OF_WEEK)
    time = models.IntegerField(default=DAWN, validators=[MinValueValidator(0), MaxValueValidator(MINUTES_IN_A_DAY - 1)])
    is_new_day = models.BooleanField(default=False)

    def __str__(self):
        return 'Clock ' + self.session.abbr_key_tag()

    def serialize(self):
        return self.display

    @property
    def display(self):
        return self.get_day_display() + ' ' + self.get_time_display()

    def get_time_display(self):
        """ Returns the time as a string in the format 'hh:mmam' or 'hh:mmpm' """
        hours = (self.time % self.MINUTES_IN_A_HALF_DAY) // 60
        if hours == 0:
            hours = 12
        minutes = self.time % 60
        suffix = 'pm' if self.time >= self.MINUTES_IN_A_HALF_DAY else 'am'

        return f"{hours}:{minutes:02d}{suffix}"

    def advance(self, amount_in_minutes):
        """ Updates the day and time by the given amount of time,
        rolling the clock and days over at midnight and end of saturday respectively. """

        self.time += amount_in_minutes

        days_to_add = self.time // self.MINUTES_IN_A_DAY
        if days_to_add > 0:
            self.time = self.time % self.MINUTES_IN_A_DAY
            self.advance_day(days_to_add)

    def advance_day(self, days_to_add):
        """ Advances the day by the given number of days, rolling over at the end of the week. """
        current_day_index = self.DAYS_OF_WEEK.index((self.day, self.get_day_display()))
        new_day_index = (current_day_index + days_to_add) % 7
        self.day = self.DAYS_OF_WEEK[new_day_index][0]
        self.is_new_day = True

    def is_now(self, day, time):
        return self.day == day and self.time == time

    def is_in_past(self, day, time):
        is_past_day = self.DAY_TO_INDEX[self.day] > self.DAY_TO_INDEX[day]
        return is_past_day or (self.day == day and self.time > time)

    def is_now_or_in_past(self, day, time):
        return self.is_now(day, time) or self.is_in_past(day, time)

    @property
    def minutes_to_midnight(self):
        return self.MINUTES_IN_A_DAY - self.time

    @property
    def minutes_to_dawn(self):
        return self.DAWN - self.time

    @property
    def minutes_to_overslept_time(self):
        return self.OVERSLEPT_TIME - self.time

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


@receiver(post_save, sender=Clock)
def time_has_passed(sender, instance, **kwargs):
    # refactor all this ish into game_logic.py
    instance.session.trigger_scheduled_events()

    if instance.is_new_day:
        if instance.day == Clock.SUNDAY:
            instance.session.game_over = True
            return
        instance.is_new_day = False

        instance.session.reset_for_new_day()

        if instance.session.hero.is_in_bed:
            instance.session.hero.is_in_bed = False
            instance.session.hero.save()

            if instance.time < instance.DAWN:
                instance.advance(instance.minutes_to_dawn)
        else:
            instance.session.message = "You passed out at midnight and overslept! You're just now waking up."
            if instance.time < instance.OVERSLEPT_TIME:
                instance.advance(instance.minutes_to_overslept_time)

        instance.save()


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


class ItemManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Item(models.Model):
    SEED = 'SEED'
    SPROUT = 'SPROUT'
    CROP = 'CROP'
    GIFT = 'GIFT'
    FISH = 'FISH'
    MINERAL = 'MINERAL'
    ARTIFACT = 'ARTIFACT'
    HERB = 'HERB'
    FLOWER = 'FLOWER'
    BERRY = 'BERRY'

    ITEM_TYPES = [
        (SEED, 'Seed'),
        (SPROUT, 'Sprout'),
        (CROP, 'Crop'),
        (GIFT, 'Gift'),
        (FISH, 'Fish'),
        (MINERAL, 'Mineral'),
        (ARTIFACT, 'Artifact'),
        (HERB, 'Herb'),
        (FLOWER, 'Flower'),
        (BERRY, 'Berry'),
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
        UNCOMMON: 0.2,
        RARE: 0.1,
        EPIC: 0.05,
    }

    CROP_PROFIT_MULTIPLIER = 10

    name = models.CharField(max_length=255, unique=True)
    icon = models.ImageField(upload_to='items/', null=True, blank=True)
    item_type = models.CharField(max_length=8, choices=ITEM_TYPES, default=GIFT)
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
            },
            'rarity': self.get_rarity_display(),
        }

    def get_next_growth_stage(self):
        next_type = self.get_next_type()
        next_name = self.get_next_name()
        next_price = self.get_next_price()

        instance, created = Item.objects.get_or_create(
                            name=next_name, item_type=next_type, price=next_price,
                            rarity=self.rarity, icon=self.icon)

        return instance

    def get_next_type(self):
        if self.item_type == Item.SEED:
            return Item.SPROUT
        elif self.item_type == Item.SPROUT:
            return Item.CROP
        else:
            raise ValueError('Item is not a seed or sprout.')

    def get_next_name(self):
        # could have some Item.name validation that ensures that the name ends with the item type for seed/sprout/crop
        curr_type_name = dict(Item.ITEM_TYPES)[self.item_type]
        next_type_name = dict(Item.ITEM_TYPES)[self.get_next_type()]
        return self.name.replace(curr_type_name, next_type_name)

    def get_next_price(self):
        # seed -> sprout is mostly irrelevant, so goal is to make seed -> crop hit the CROP_PROFIT_MULTIPLIER
        # let's be ridiculous and say that seeds and sprouts are =, and then you multiply when you get to the crop

        if self.item_type == Item.SEED:
            return self.price
        elif self.item_type == Item.SPROUT:
            return self.price * self.CROP_PROFIT_MULTIPLIER
        else:
            raise ValueError('Item is not a seed or sprout.')


class ItemToken(models.Model):
    session = models.ForeignKey('Session', on_delete=models.CASCADE, related_name='item_tokens')
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='tokens')
    has_been_watered = models.BooleanField(default=False)

    def __str__(self):
        return self.item.name + ' ' + self.session.abbr_key_tag()

    def serialize(self):
        return {
            'name': self.name,
            'rarity': self.item.get_rarity_display(),
            'has_been_watered': self.has_been_watered,
        }

    @property
    def name(self):
        return self.item.name

    @property
    def item_type(self):
        return self.item.item_type

    @property
    def rarity(self):
        return self.item.rarity

    @property
    def price(self):
        return self.item.price


class PlaceManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class ScheduledEvent(models.Model):
    ITEMS_APPEAR = 'ITEMS_APPEAR'

    EVENT_TYPES = [
        (ITEMS_APPEAR, 'Items appear'),
    ]

    day = models.CharField(default=Clock.SUNDAY, max_length=9, choices=Clock.DAYS_OF_WEEK)
    time = models.IntegerField(default=Clock.DAWN,
                               validators=[MinValueValidator(0), MaxValueValidator(Clock.MINUTES_IN_A_DAY - 1)])

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

    ITEM_POOL_TYPE_MAP = {
        MOUNTAIN: [Item.MINERAL, Item.ARTIFACT],
        BEACH: [Item.FISH],
        FOREST: [Item.HERB, Item.FLOWER, Item.BERRY],
    }

    place_type = models.CharField(max_length=8, choices=PLACE_TYPES, default=TOWN)

    default_items = models.ManyToManyField('Item', blank=True)

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

    def save(self, *args, **kwargs):
        if self._state.adding:
            # save place state first so we can have id and assign item_pool
            super().save(*args, **kwargs)
            self.populate_item_pool()
        else:
            super().save(*args, **kwargs)

    @property
    def is_farmhouse(self):
        try:
            is_building_on_farm = self.building.surround.pk == Place.get_default_pk()
            return is_building_on_farm and self.place_type == Place.HOME
        except Building.DoesNotExist:
            return False

    def populate_item_pool(self):
        """ Populates the item pool by filtering on item types based on this place type. """
        item_types = self.ITEM_POOL_TYPE_MAP.get(self.place_type)
        if item_types is None:
            return

        all_items_of_correct_types = Item.objects.filter(item_type__in=item_types)
        self.item_pool.set(all_items_of_correct_types)


class Building(Place):
    surround = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='buildings')

    def __str__(self):
        return super().__str__()

    def serialize(self):
        return super().serialize()


class PlaceState(models.Model):
    session = models.ForeignKey('Session', on_delete=models.CASCADE, related_name='place_states')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='states')

    item_tokens = models.ManyToManyField('ItemToken', blank=True)
    occupants = models.ManyToManyField('Villager', blank=True)

    def __str__(self):
        return f'{self.place} state ' + self.session.abbr_key_tag()

    def save(self, *args, **kwargs):
        if self._state.adding:
            # save place state first so we can have id and assign contents and occupants
            super().save(*args, **kwargs)

            # set contents and occupants based on place defaults

            item_token_objs = [ItemToken(session=self.session, item=item) for item in self.place.default_items.all()]
            item_tokens = ItemToken.objects.bulk_create(item_token_objs)
            self.item_tokens.set(item_tokens)

            try:
                building = self.place.building
                self.occupants.set(building.residents.all())
            except Building.DoesNotExist:
                pass
        else:
            super().save(*args, **kwargs)


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

        place_state = self.place_states.get(place=event.place)

        place_state.item_tokens.set(item_tokens)

    def reset_for_new_day(self):
        self.reset_villager_states()
        self.grow_crops()

    def reset_villager_states(self):
        self.villager_states.all().update(has_been_talked_to=False, has_been_given_gift=False)

    def grow_crops(self):
        """Find all seeds/sprouts in the farm and "grow" them if they've been watered --
        ie replace them with a new item token at the next growth stage."""
        farm_state = self.place_states.get(place__place_type=Place.FARM)
        item_tokens = farm_state.item_tokens.all()
        new_contents = []

        for token in item_tokens:
            if token.item_type not in [Item.SEED, Item.SPROUT]:
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

    koin_earned = models.IntegerField(default=0)
    hearts_earned = models.IntegerField(default=0)

    is_in_bed = models.BooleanField(default=False)

    def __str__(self):
        return 'Hero ' + self.session.abbr_key_tag()

    def serialize(self):
        return {
            'score': self.score,
            'koin_earned': self.koin_earned,
            'hearts_earned': self.hearts_earned,
        }

    @property
    def score(self):
        return self.koin_earned * self.hearts_earned * 10


class ItemTypePreference(models.Model):
    LOVE = 'LOVE'
    LIKE = 'LIKE'
    NEUTRAL = 'NEUTRAL'
    DISLIKE = 'DISLIKE'
    HATE = 'HATE'

    VALENCES = [
        (LOVE, 'love'),
        (LIKE, 'like'),
        (NEUTRAL, 'neutral'),
        (DISLIKE, 'dislike'),
        (HATE, 'hate'),
    ]

    UNIVERSAL_PREFERENCES = {
        Item.CROP: LIKE,
        Item.FLOWER: LIKE,
        Item.BERRY: LIKE,
        Item.SEED: DISLIKE,
        Item.SPROUT: DISLIKE,
        Item.FISH: DISLIKE,
        Item.HERB: DISLIKE,
    }

    item_type = models.CharField(max_length=8, choices=Item.ITEM_TYPES)
    valence = models.CharField(max_length=7, choices=VALENCES, default=NEUTRAL)

    def __str__(self):
        return f'preference: {self.get_valence_display()}s {self.get_item_type_display()}s'

    @classmethod
    def get_or_create_from_string(cls, string):
        # in our data intake, expect to have inputs like 'BERRY: LOVE'
        # so get_or_create a new instance from a string
        item_type, valence = string.split(': ')
        item_type = item_type.upper()
        valence = valence.upper()

        if item_type not in dict(Item.ITEM_TYPES):
            raise ValueError(f'invalid item type: {item_type}')

        if valence not in dict(cls.VALENCES):
            raise ValueError(f'invalid valence: {valence}')

        return cls.objects.get_or_create(item_type=item_type, valence=valence)


class VillagerManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Villager(models.Model):
    name = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    friendliness = models.IntegerField(default=4, validators=[MinValueValidator(1), MaxValueValidator(7)])
    portrait = models.ImageField(upload_to='portraits/', null=True, blank=True, default='portraits/squall-farmer.png')
    home = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True, related_name='residents')

    item_type_preferences = models.ManyToManyField('ItemTypePreference', blank=True, related_name='preferred_by')

    objects = VillagerManager()

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

    def gift_valence(self, item):
        """return how villager feels about a gift"""
        try:
            preference = self.item_type_preferences.get(item_type=item.item_type)
            return preference.valence
        except ItemTypePreference.DoesNotExist:
            try:
                valence = ItemTypePreference.UNIVERSAL_PREFERENCES[item.item_type]
                return valence
            except KeyError:
                return ItemTypePreference.NEUTRAL

    def get_dialogue(self, trigger, affinity_tier=None):
        """return a dialogue object for a given trigger and affinity tier"""
        try:
            dialogue = self.dialogue_lines.get(trigger=trigger, affinity_tier=affinity_tier)
        except DialogueLine.DoesNotExist:
            raise DialogueLine.DoesNotExist(f'no dialogue for {self.name} with trigger {trigger} and affinity tier {affinity_tier}')

        return dialogue

    @property
    def talk_duration(self):
        FRIENDLINESS_TO_TALK_DURATION = {
            1: 5,
            2: 10,
            3: 15,
            4: 30,
            5: 45,
            6: 60,
            7: 90,
        }
        return FRIENDLINESS_TO_TALK_DURATION[self.friendliness]


class VillagerState(models.Model):
    MAX_AFFINITY = 100
    AFFINITY_TIER_SIZE = 20
    TOTAL_TIERS = MAX_AFFINITY // AFFINITY_TIER_SIZE

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='villager_states')
    villager = models.ForeignKey(Villager, on_delete=models.CASCADE, related_name='states')

    affinity = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(MAX_AFFINITY)])
    location = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='villagers')  # , default=villager.home)

    has_been_talked_to = models.BooleanField(default=False)
    has_ever_been_talked_to = models.BooleanField(default=False)
    has_been_given_gift = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.villager} state ' + self.session.abbr_key_tag()

    def serialize(self):
        return {
            'villager': self.villager.serialize(),
            'display_affinity': self.display_affinity,
            'location': self.location.serialize(),
        }

    @property
    def display_affinity(self):
        tier = self.affinity // self.AFFINITY_TIER_SIZE  # 0-5

        full_hearts = ['❤️' for _ in range(tier)]
        empty_hearts = ['🖤' for _ in range(self.TOTAL_TIERS - tier)]

        return ''.join(full_hearts + empty_hearts)

    def add_affinity(self, amount):
        self.affinity += amount

        if self.affinity > 100:
            self.affinity = 100

        if self.affinity < 0:
            self.affinity = 0

        self.save()
        return self.affinity


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
    SLP = 'SLEEP'

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
        (SLP, 'Sleep'),
    ]

    MIN = 'MINUTE'
    HOUR = 'HOUR'
    DAY = 'DAY'
    KOIN = 'KOIN'

    HOUR_ABBR = 'hr'
    MIN_ABBR = 'min'
    KOIN_SIGN = '⚜️'

    COST_UNITS = [
        (MIN, MIN_ABBR),
        (HOUR, HOUR_ABBR),
        (KOIN, KOIN_SIGN),
    ]

    TIME_UNITS = [MIN, HOUR, DAY]
    MONEY_UNITS = [KOIN]

    action_type = models.CharField(max_length=7, choices=ACTION_TYPES)
    description = models.CharField(max_length=255)

    cost_amount = models.IntegerField(default=1)
    cost_unit = models.CharField(max_length=6, choices=COST_UNITS)

    # let's be real: we should have a target_item (nullable), target_villager (nullable), and target_location (nullable)
    # goofy over-engineered content_type should be nixed

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
        elif self.cost_amount > 60 and self.cost_unit == self.MIN:
            if self.cost_amount % 60 == 0:
                return f'{self.cost_amount // 60}{self.HOUR_ABBR}'
            else:
                return f'{self.cost_amount // 60}{self.HOUR_ABBR} ' \
                       f'{self.cost_amount % 60}{self.MIN_ABBR}'
        else:
            return str(self.cost_amount) + self.get_cost_unit_display()

    def is_cost_in_money(self):
        return self.cost_unit in self.MONEY_UNITS

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class DialogueLine(models.Model):
    LOVED_GIFT = 'LOVED_GIFT'
    LIKED_GIFT = 'LIKED_GIFT'
    NEUTRAL_GIFT = 'NEUTRAL_GIFT'
    DISLIKED_GIFT = 'DISLIKED_GIFT'
    HATED_GIFT = 'HATED_GIFT'
    FIRST_MEETING = 'FIRST_MEETING'
    TALKED_TO = 'TALKED_TO'

    DIALOGUE_TRIGGERS = [
        (LOVED_GIFT, 'Loved Gift'),
        (LIKED_GIFT, 'Liked Gift'),
        (NEUTRAL_GIFT, 'Neutral Gift'),
        (DISLIKED_GIFT, 'Disliked Gift'),
        (HATED_GIFT, 'Hated Gift'),
        (FIRST_MEETING, 'First Meeting'),
        (TALKED_TO, 'Talked To'),
    ]

    speaker = models.ForeignKey(Villager, on_delete=models.CASCADE, related_name='dialogue_lines')
    affinity_tier = models.IntegerField(null=True, blank=True)
    trigger = models.CharField(max_length=13, choices=DIALOGUE_TRIGGERS, default=TALKED_TO)
    full_text = models.TextField()

    def __str__(self):
        return f'{self.speaker.name} says: {self.abbr_text}'

    def serialize(self):
        return {
            'speaker': self.speaker.serialize(),
            'full_text': self.full_text,
        }

    @property
    def abbr_text(self):
        return f"{self.full_text[:50]}{'...' if len(self.full_text) > 50 else ''}"
