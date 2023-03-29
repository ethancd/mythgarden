from django.db import models
from django.templatetags.static import static

from ._constants import PLACE_TYPES, FARM, TOWN, MOUNTAIN, FOREST, BEACH, HOME, MINERAL, FOSSIL, FISH, HERB, FLOWER, \
    BERRY, TECHNO, MAGIC, IMAGE_PREFIX, PLACE_IMAGE_DIR, SHOP
from .item import Item, ItemToken


class PlaceManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Place(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image_path = models.CharField(max_length=255, default='farm-unsplash.jpeg')

    ITEM_POOL_TYPE_MAP = {
        MOUNTAIN: [MINERAL, FOSSIL, TECHNO, MAGIC],
        BEACH: [FISH],
        FOREST: [HERB, FLOWER, BERRY],
    }

    place_type = models.CharField(max_length=8, choices=PLACE_TYPES, default=TOWN)
    has_inventory = models.BooleanField(default=False)

    item_pool = models.ManyToManyField('Item', blank=True, related_name='pool_locations')

    objects = PlaceManager()

    @classmethod
    def get_default_pk(cls):
        place, created = cls.objects.get_or_create(name='The Farm', place_type=FARM, has_inventory=True)
        return place.pk

    @classmethod
    def get_default_shop_pk(cls):
        place, created = cls.objects.get_or_create(name='mom and pop shop', place_type=SHOP, has_inventory=True)
        return place.pk

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            'name': self.name,
            'imageUrl': self.image_url,
            'id': self.id,
            'hasInventory': self.has_inventory
        }

    @property
    def image_url(self):
        if not self.image_path:
            return None

        return static(f'{IMAGE_PREFIX}/{PLACE_IMAGE_DIR}/{self.image_path}')

    def save(self, *args, **kwargs):
        if self._state.adding:
            # save place state first so we can have id and assign item_pool
            super().save(*args, **kwargs)
            self.populate_item_pool()
        else:
            super().save(*args, **kwargs)

    @property
    def is_farmhouse(self):
        try:
            is_building_on_farm = self.building.surround.pk == Place.get_default_pk()
            return is_building_on_farm and self.place_type == HOME
        except Building.DoesNotExist:
            return False

    def populate_item_pool(self):
        """ Populates the item pool by filtering on item types based on this place type. """
        item_types = self.ITEM_POOL_TYPE_MAP.get(self.place_type)
        if item_types is None:
            return

        all_items_of_correct_types = Item.objects.filter(item_type__in=item_types)
        self.item_pool.set(all_items_of_correct_types)


class Building(Place):
    surround = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='buildings')

    def __str__(self):
        return super().__str__()

    def serialize(self):
        return super().serialize()

    class Meta:
        ordering = ['name']


class PlaceState(models.Model):
    session = models.ForeignKey('Session', on_delete=models.CASCADE, related_name='place_states')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='states')

    item_tokens = models.ManyToManyField('ItemToken', blank=True)
    # would be nice to have a validator that said "if placeState.place.has_inventory == False, then item_tokens has to be empty" basically

    def __str__(self):
        return f'{self.place} state ' + self.session.abbr_key_tag()
