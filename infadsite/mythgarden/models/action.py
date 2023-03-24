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
            GATHER_DESCRIPTION_MAP = {
                FISHING_DESCRIPTION: self.FISHING,
                DIGGING_DESCRIPTION: self.DIGGING,
                FORAGING_DESCRIPTION: self.FORAGING,
            }
            gather_type = GATHER_DESCRIPTION_MAP[self.description]
            return self.ACTION_EMOJIS[self.GATHER][gather_type]
        elif self.action_type == self.TRAVEL:
            travel_type = self.get_travel_type_of_action()
            return self.ACTION_EMOJIS[self.TRAVEL][travel_type]
        else:
            return self.ACTION_EMOJIS[self.action_type]

    def get_travel_type_of_action(self):
        if self.description == EXIT_DESCRIPTION:
            return self.EXIT
        elif 'Enter' in self.description:
            return self.ENTER
        else:
            return self.TRAVEL

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

    @property
    def unique_digest(self):
        pks = [f'{target.pk}' for target in [self.target_item, self.target_villager, self.target_place] if target]

        return f'{self.action_type}-{"-".join(pks)}'

    @property
    def target_count(self):
        return sum(1 for t in [self.target_item, self.target_villager, self.target_place] if t)

    def is_cost_in_money(self):
        return self.cost_unit in self.MONEY_UNITS
