from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.templatetags.static import static

from .item_type_preference import ItemTypePreference
from .place import Place, Building
from .dialogue import DialogueLine

from ._constants import NEUTRAL, IMAGE_PREFIX

class VillagerManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Villager(models.Model):
    name = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    friendliness = models.IntegerField(default=4, validators=[MinValueValidator(1), MaxValueValidator(7)])
    image_path = models.CharField(max_length=255, default='portraits/squall-farmer.png', null=True, blank=True)
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
            'image_url': self.image_url
        }

    @property
    def image_url(self):
        if not self.image_path:
            return None

        return static(f'{IMAGE_PREFIX}{self.image_path}')

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
                return NEUTRAL

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

    session = models.ForeignKey('Session', on_delete=models.CASCADE, related_name='villager_states')
    villager = models.ForeignKey('Villager', on_delete=models.CASCADE, related_name='states')

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
            'affinity': self.display_affinity,
            'name': self.villager.name,
            'image_url': self.villager.image_url,
            'description': self.villager.description,
            'id': self.villager.id,
            'location': self.location.serialize(),
        }

    @property
    def display_affinity(self):
        full_hearts = ['❤️' for _ in range(self.affinity_tier)]
        empty_hearts = ['🖤' for _ in range(self.TOTAL_TIERS - self.affinity_tier)]

        return ''.join(full_hearts + empty_hearts)

    @property
    def affinity_tier(self):
        return self.affinity // self.AFFINITY_TIER_SIZE

    def add_affinity(self, amount):
        self.affinity += amount

        if self.affinity > 100:
            self.affinity = 100

        if self.affinity < 0:
            self.affinity = 0

        self.save()
        return self.affinity

    def mark_as_talked_to(self):
        self.has_been_talked_to = True
        self.has_ever_been_talked_to = True
        self.save()
