from django.db import models

from ._constants import DIRECTIONS, KOIN_SIGN, FISHING_DESCRIPTION, DIGGING_DESCRIPTION, FORAGING_DESCRIPTION, \
    EXIT_DESCRIPTION


class Action(models.Model):
    TRAVEL = 'TRAVEL'
    TALK = 'TALK'
    GIVE = 'GIVE'
    WATER = 'WATER'
    PLANT = 'PLANT'
    HARVEST = 'HARVEST'
    BUY = 'BUY'
    SELL = 'SELL'
    STOW = 'STOW'
    RETRIEVE = 'RETRIEVE'
    GATHER = 'GATHER'
    SLEEP = 'SLEEP'

    ENTER = 'ENTER'
    EXIT = 'EXIT'

    FISHING = 'FISHING'
    DIGGING = 'DIGGING'
    FORAGING = 'FORAGING'

    ACTION_EMOJIS = {
        TRAVEL: {
            TRAVEL: '🚶',
            ENTER: '🏠',
            EXIT: '🚪',
        },
        TALK: '💬',
        GIVE: '🎁',
        WATER: '💧',
        PLANT: '🌰',
        HARVEST: '🌾',
        BUY: '🛒',
        SELL: '💰',
        STOW: '📦',
        RETRIEVE: '🎒',
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
        (STOW, 'Stow'),
        (RETRIEVE, 'Retrieve'),
        (GATHER, 'Gather'),
        (SLEEP, 'Sleep'),
    ]

    MIN = 'MINUTE'
    HOUR = 'HOUR'
    KOIN = 'KOIN'

    HOUR_ABBR = 'hr'
    MIN_SIGN = '🕒'

    COST_UNITS = [
        (MIN, MIN_SIGN),
        (HOUR, HOUR_ABBR),
        (KOIN, KOIN_SIGN),
    ]

    TIME_UNITS = [MIN, HOUR]
    MONEY_UNITS = [KOIN]

    action_type = models.CharField(max_length=8, choices=ACTION_TYPES)
    description = models.CharField(max_length=255)

    cost_amount = models.IntegerField(default=1, null=True, blank=True)
    cost_unit = models.CharField(max_length=6, choices=COST_UNITS, null=True, blank=True)

    target_item = models.ForeignKey('ItemToken', on_delete=models.CASCADE, null=True, blank=True)
    target_villager = models.ForeignKey('Villager', on_delete=models.CASCADE, null=True, blank=True)
    target_place = models.ForeignKey('Place', on_delete=models.CASCADE, null=True, blank=True)

    direction = models.CharField(max_length=5, choices=DIRECTIONS, null=True, blank=True)

    log_statement = models.CharField(
        max_length=255)  # this should really be generated from the action_type, direct objects, etc

    def __str__(self):
        return self.description

    def serialize(self):
        return {
            'description': self.description,
            'displayCost': self.display_cost,
            'emoji': self.emoji,
            'uniqueDigest': self.unique_digest,
            'targetCount': self.target_count
        }

    @property
    def emoji(self):
        if self.action_type == self.GATHER:
            gather_type = self.get_gather_type_of_action()
            return self.ACTION_EMOJIS[self.GATHER][gather_type]
        elif self.action_type == self.TRAVEL:
            travel_type = self.get_travel_type_of_action()
            return self.ACTION_EMOJIS[self.TRAVEL][travel_type]
        else:
            return self.ACTION_EMOJIS[self.action_type]

    def get_gather_type_of_action(self):
        GATHER_DESCRIPTION_MAP = {
            FISHING_DESCRIPTION: self.FISHING,
            DIGGING_DESCRIPTION: self.DIGGING,
            FORAGING_DESCRIPTION: self.FORAGING,
        }

        return GATHER_DESCRIPTION_MAP[self.description]

    def get_travel_type_of_action(self):
        if self.description == EXIT_DESCRIPTION:
            return self.EXIT
        elif 'Enter' in self.description:
            return self.ENTER
        else:
            return self.TRAVEL

    @property
    def display_cost(self):
        if not self.cost_amount or not self.cost_unit:
            return ''

        if self.is_cost_in_money():
            return self.get_cost_unit_display() + str(self.cost_amount)
        else:
            return str(self.cost_amount) + self.get_cost_unit_display()

    @property
    def unique_digest(self):
        pks = [f'{target.pk}' for target in [self.target_item, self.target_villager, self.target_place] if target]

        return f'{self.action_type}-{"-".join(pks)}'

    @property
    def target_count(self):
        return sum(1 for t in [self.target_item, self.target_villager, self.target_place] if t)

    def is_cost_in_money(self):
        return self.cost_unit in self.MONEY_UNITS
