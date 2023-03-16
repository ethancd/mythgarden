from django.db import models
from django.templatetags.static import static

from ._constants import IMAGE_PREFIX


class Hero(models.Model):
    name = models.CharField(max_length=255, default='New Farmer')
    image_path = models.CharField(max_length=255, default='portraits/default.png')

    high_score = models.IntegerField(default=0)
    boost_level = models.IntegerField(default=0)

    def set_high_score(self, new_score):
        if new_score > self.high_score:
            self.high_score = new_score
            self.save()
            return True
        else:
            return False

    @property
    def image_url(self):
        if not self.image_path:
            return None

        return static(f'{IMAGE_PREFIX}{self.image_path}')


class HeroState(models.Model):
    session = models.OneToOneField('Session', on_delete=models.CASCADE, primary_key=True, related_name='hero_state')
    hero = models.OneToOneField('Hero', on_delete=models.CASCADE)

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
            'imageUrl': self.hero.image_url,
            'boostLevel': self.hero.boost_level
        }

    @property
    def score(self):
        return self.koin_earned * self.hearts_earned * 10
