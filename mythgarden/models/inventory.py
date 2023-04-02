from django.db import models


class Inventory(models.Model):
    session = models.OneToOneField('Session', on_delete=models.CASCADE, primary_key=True)
    item_tokens = models.ManyToManyField('ItemToken', blank=True)

    def __str__(self):
        return 'Inventory ' + self.session.abbr_key_tag()
