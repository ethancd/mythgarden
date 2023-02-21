from django.db import models
from django.templatetags.static import static

from ._constants import IMAGE_PREFIX


class Hero(models.Model):
    session = models.OneToOneField('Session', on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255, default='Squall')
    image_path = models.CharField(max_length=255, default='portraits/squall-farmer.png')

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
    def image_url(self):
        if not self.image_path:
            return None

        return static(f'{IMAGE_PREFIX}{self.image_path}')

    @property
    def score(self):
        return self.koin_earned * self.hearts_earned * 10
