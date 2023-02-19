from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from ._constants import DIRECTIONS, KOIN_SIGN, FISHING_DESCRIPTION, DIGGING_DESCRIPTION, FORAGING_DESCRIPTION


class Action(models.Model):
    TRAVEL = 'TRAVEL'
    TALK = 'TALK'
    GIVE = 'GIVE'
    WATER = 'WATER'
    PLANT = 'PLANT'
    HARVEST = 'HARVEST'
    BUY = 'BUY'
    SELL = 'SELL'
    GATHER = 'GATHER'
    SLEEP = 'SLEEP'

    FISHING = 'FISHING'
    DIGGING = 'DIGGING'
    FORAGING = 'FORAGING'

    ACTION_EMOJIS = {
        TRAVEL: '🚶',
        TALK: '💬',
        GIVE: '🎁',
        WATER: '💧',
        PLANT: '🌱',
        HARVEST: '🌾',
        BUY: '🛒',
        SELL: '💰',
        GATHER: {
            FISHING: '🎣',
            DIGGING: '⛏',
            FORAGING: '🌲',
        },
        SLEEP: '💤',
    }

    ACTION_TYPES = [
        (TRAVEL, 'Travel'),
        (TALK, 'Talk'),
        (GIVE, 'Give'),
        (PLANT, 'Plant'),
        (WATER, 'Water'),
        (HARVEST, 'Harvest'),
        (BUY, 'Buy'),
        (SELL, 'Sell'),
        (GATHER, 'Gather'),
        (SLEEP, 'Sleep'),
    ]

    MIN = 'MINUTE'
    HOUR = 'HOUR'
    DAY = 'DAY'
    KOIN = 'KOIN'

    HOUR_ABBR = 'hr'
    MIN_ABBR = 'min'

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

    direction = models.CharField(max_length=5, choices=DIRECTIONS, null=True, blank=True)

    log_statement = models.CharField(
        max_length=255)  # this should really be generated from the action_type, direct objects, etc

    def __str__(self):
        return self.description

    def serialize(self):
        return {
            'description': self.description,
            'display_cost': self.display_cost,
            'emoji': self.emoji,
        }

    @property
    def emoji(self):
        if self.action_type == self.GATHER:
            GATHER_DESCRIPTION_MAP = {
                FISHING_DESCRIPTION: self.FISHING,
                DIGGING_DESCRIPTION: self.DIGGING,
                FORAGING_DESCRIPTION: self.FORAGING,
            }
            gather_type = GATHER_DESCRIPTION_MAP[self.description]
            return self.ACTION_EMOJIS[self.GATHER][gather_type]
        else:
            return self.ACTION_EMOJIS[self.action_type]



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
