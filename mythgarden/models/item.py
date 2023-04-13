from django.db import models

from ._constants import ITEM_EMOJIS, COMMON, GIFT, ITEM_TYPES, RARITY_CHOICES, SEED, SPROUT, CROP, CROP_PROFIT_MULTIPLIER


class ItemManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Item(models.Model):
    name = models.CharField(max_length=255, unique=True)
    icon = models.ImageField(upload_to='items/', null=True, blank=True)
    item_type = models.CharField(max_length=8, choices=ITEM_TYPES, default=GIFT)
    price = models.IntegerField(default=1)
    rarity = models.CharField(max_length=8, choices=RARITY_CHOICES, default=COMMON)

    growth_days = models.IntegerField(null=True, blank=True)  # only defined for plants (seeds/sprouts/crops)
    effort_time = models.IntegerField(null=True, blank=True)  # only defined for plants (seeds/sprouts/crops)

    objects = ItemManager()

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            'name': self.name,
            'icon': {
                'url': self.icon.url if self.icon else None
            },
            'rarity': self.get_rarity_display(),
        }

    @property
    def emoji(self):
        return ITEM_EMOJIS[self.item_type]

    def get_next_growth_stage(self, days_growing):
        """Get the next item that a seed/sprout grows into, taking into account how long this item takes to grow
        and how many days it's been in the ground"""
        
        next_type = self.get_next_type(days_growing)
        next_name = self.get_next_name(next_type)
        next_price = self.get_next_price(next_type)

        instance, created = Item.objects.get_or_create(
                            name=next_name, item_type=next_type, price=next_price,
                            rarity=self.rarity, icon=self.icon)

        return instance

    def get_next_type(self, days_growing):
        if days_growing >= self.growth_days:
            return CROP
        else:
            return SPROUT

    def get_next_name(self, next_type):
        # could have some Item.name validation that ensures that the name ends with the item type for seed/sprout/crop
        # e.g. Parsnip Seed -> Parsnip Sprout -> Parsnip

        curr_type_name = dict(ITEM_TYPES)[self.item_type]
        next_type_name = dict(ITEM_TYPES)[next_type]
        
        if next_type == CROP:
            return self.name.replace(f' {curr_type_name}', '')
        else:
            return self.name.replace(curr_type_name, next_type_name)

    def get_next_price(self, next_type):
        # seed -> sprout is mostly irrelevant, so goal is to make seed -> crop hit the CROP_PROFIT_MULTIPLIER
        # let's be ridiculous and say that seeds and sprouts are =, and then you multiply when you get to the crop

        if next_type == CROP:
            return self.price * CROP_PROFIT_MULTIPLIER
        else:
            return self.price


class ItemToken(models.Model):
    session = models.ForeignKey('Session', on_delete=models.CASCADE, related_name='item_tokens')
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='tokens')
    bought_from_store = models.BooleanField(default=False)
    quantity = models.IntegerField(null=True, blank=True)

    has_been_watered = models.BooleanField(default=False)  # only defined for plants (seeds/sprouts/crops)
    days_growing = models.IntegerField(null=True, blank=True)  # only defined for plants (seeds/sprouts/crops)

    def __str__(self):
        return self.item.name + ' ' + self.session.abbr_key_tag()

    def serialize(self):
        return {
            'name': self.name,
            'rarity': self.item.get_rarity_display(),
            'emoji': self.emoji,
            'hasBeenWatered': self.has_been_watered,
            'id': self.id,
            'quantity': self.quantity
        }

    def make_copy(self):
        return ItemToken(session=self.session, item=self.item)

    @property
    def name(self):
        return self.item.name

    @property
    def item_type(self):
        return self.item.item_type

    @property
    def rarity(self):
        return self.item.rarity

    @property
    def price(self):
        return self.item.price

    @property
    def emoji(self):
        return self.item.emoji

    class Meta:
        ordering = ['pk']
