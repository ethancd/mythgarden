from django.db import models


class Hero(models.Model):
    session = models.OneToOneField('Session', on_delete=models.CASCADE, primary_key=True)
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
