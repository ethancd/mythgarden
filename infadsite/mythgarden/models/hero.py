from django.db import models

from ._constants import DEFAULT_PORTRAIT
from .farmer_portrait import FarmerPortrait


class Hero(models.Model):
    name = models.CharField(max_length=16, default='New Farmer')
    portrait = models.ForeignKey(FarmerPortrait, on_delete=models.SET_DEFAULT, default=FarmerPortrait.get_default_pk)

    high_score = models.IntegerField(default=0)
    boost_level = models.IntegerField(default=0)

    @classmethod
    def get_default_pk(cls):
        new_hero = cls.objects.create()
        return new_hero.pk

    def set_high_score(self, new_score):
        if new_score > self.high_score:
            self.high_score = new_score
            self.save()
            return True
        else:
            return False

    @property
    def is_default_name(self):
        return self.name == 'New Farmer'

    @property
    def is_default_portrait(self):
        if not self.portrait:
            return False

        return self.portrait.image_path == DEFAULT_PORTRAIT

    @property
    def image_url(self):
        if not self.portrait:
            return None

        return self.portrait.image_url


class HeroState(models.Model):
    session = models.OneToOneField('Session', on_delete=models.CASCADE, primary_key=True, related_name='hero_state')
    hero = models.ForeignKey('Hero', on_delete=models.CASCADE, default=Hero.get_default_pk, null=True)

    koin_earned = models.IntegerField(default=0)
    hearts_earned = models.IntegerField(default=0)
    is_in_bed = models.BooleanField(default=False)

    def __str__(self):
        return 'Hero ' + self.session.abbr_key_tag()

    def serialize(self):
        return {
            'score': self.score,
            'highScore': self.hero.high_score,
            'koinEarned': self.koin_earned,
            'heartsEarned': self.hearts_earned,
            'name': self.hero.name,
            'isDefaultName': self.hero.is_default_name,
            'isDefaultPortrait': self.hero.is_default_portrait,
            'imageUrl': self.hero.image_url,
            'boostLevel': self.hero.boost_level
        }

    @property
    def score(self):
        return self.koin_earned * self.hearts_earned * 10
