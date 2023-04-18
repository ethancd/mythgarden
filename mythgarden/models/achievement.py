from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from ._constants import ACHIEVEMENT_TYPES, ACHIEVEMENT_TRIGGER_TYPES, GATHER, ACHIEVEMENT_EMOJIS, BEST_FRIENDS, \
    FAST_FRIENDS, STEADFAST_FRIENDS


class Achievement(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    achievement_type = models.CharField(max_length=24, choices=ACHIEVEMENT_TYPES)
    trigger_type = models.CharField(max_length=24, choices=ACHIEVEMENT_TRIGGER_TYPES)
    threshold = models.IntegerField(null=True, blank=True)
    threshold_day_number = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(6)])

    villager = models.ForeignKey('Villager', on_delete=models.CASCADE, null=True, blank=True)

    @property
    def emoji(self):
        if self.trigger_type == GATHER:
            return ACHIEVEMENT_EMOJIS[GATHER][self.achievement_type]
        else:
            return ACHIEVEMENT_EMOJIS[self.trigger_type]

    @property
    def unlocked_message(self):
        return f"🎉 Achievement Unlocked: {self.name}!"

    @classmethod
    def check_triggered_achievements(cls, trigger_type, session, *args, **kwargs):
        achievements = cls.objects.filter(trigger_type=trigger_type)

        return cls.check_achievements(achievements, session, *args, **kwargs)

    @classmethod
    def check_achievements(cls, achievements, session, *args, **kwargs):
        already_earned = session.hero.achievements.select_related('villager').all()
        notched_count = 0

        for achievement in achievements:
            if achievement in already_earned:
                continue

            achieved = achievement.check_if_completed(*args, **kwargs)

            if achieved:
                session.hero.achievements.add(achievement)
                session.messages.create(achievement.unlocked_message)
                notched_count += 1

        return notched_count

    def check_if_completed(self, *args, **kwargs):
        ck = f'check_{self.achievement_type.lower()}'

        if hasattr(self, ck) and callable(getattr(self, ck)):
            return getattr(self, ck)(*args, **kwargs)

    # trigger_type GAIN_HEARTS
    def check_all_villagers_hearts(self, villager_states, *args, **kwargs):
        min_hearts = min([v_state.affinity_tier for v_state in villager_states])

        return min_hearts >= self.threshold

    def check_multiple_best_friends(self, villager_states, *args, **kwargs):
        best_friends = [v_state for v_state in villager_states if v_state.is_bestie]

        return len(best_friends) >= self.threshold

    def check_best_friends(self, villager_state, *args, **kwargs):
        is_right_villager = villager_state.villager == self.villager

        return villager_state.is_bestie and is_right_villager

    def check_fast_friends(self, villager_state, clock, *args, **kwargs):
        is_right_villager = villager_state.villager == self.villager
        is_fast = clock.day_index <= self.threshold_day_number

        return is_fast and villager_state.is_bestie and is_right_villager

    # trigger_type TALKED_TO_VILLAGERS
    def check_steadfast_friends(self, villager_state, *args, **kwargs):
        is_right_villager = villager_state.villager == self.villager
        is_steadfast = villager_state.talked_to_count == self.threshold

        return is_steadfast and is_right_villager

    # trigger_type GAIN_ACHIEVEMENT
    def check_bestest_friends(self, hero):
        achievement_count = hero.achievements.filter(achievement_type=BEST_FRIENDS).count()

        return achievement_count >= self.threshold

    def check_fastest_friends(self, hero):
        achievement_count = hero.achievements.filter(achievement_type=FAST_FRIENDS).count()

        return achievement_count >= self.threshold

    def check_steadfastest_friends(self, hero):
        achievement_count = hero.achievements.filter(achievement_type=STEADFAST_FRIENDS).count()

        return achievement_count >= self.threshold

    # trigger_type EARN_MONEY
    def check_gross_income(self, hero_state, *args, **kwargs):
        return hero_state.koin_earned >= self.threshold

    def check_fast_cash(self, hero_state, clock, *args, **kwargs):
        earned_enough = hero_state.koin_earned >= self.threshold
        fast_enough = clock.day_index <= self.threshold_day_number

        return earned_enough and fast_enough

    def check_balanced_income(self, hero_state, *args, **kwargs):
        min_income = min([
            hero_state.farming_koin_earned,
            hero_state.mining_koin_earned,
            hero_state.fishing_koin_earned,
            hero_state.foraging_koin_earned
        ])

        return min_income >= self.threshold

    # trigger_type HARVEST
    def check_farming_intake(self, hero_state):
        return hero_state.farming_intake >= self.threshold

    # trigger_type GATHER
    def check_mining_intake(self, hero_state):
        return hero_state.mining_intake >= self.threshold

    def check_fishing_intake(self, hero_state):
        return hero_state.fishing_intake >= self.threshold

    def check_foraging_intake(self, hero_state):
        return hero_state.foraging_intake >= self.threshold

    def __str__(self):
        return f"{self.name}: {self.description}"

    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'emoji': self.emoji,
            'id': self.id
        }
