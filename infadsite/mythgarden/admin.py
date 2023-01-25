from django.contrib import admin

from .models import Hero, Rucksack, Clock, Wallet, Situation, Place, Landmark, Bridge, Item


class ClockInline(admin.TabularInline):
    model = Clock
    max_num = 1


class WalletInline(admin.TabularInline):
    model = Wallet
    max_num = 1


class SituationInline(admin.TabularInline):
    model = Situation
    max_num = 1


class LandmarkInline(admin.TabularInline):
    model = Landmark
    extra = 1


class Bridge1Inline(admin.TabularInline):
    model = Bridge
    fk_name = 'place_1'
    extra = 1


class Bridge2Inline(admin.TabularInline):
    model = Bridge
    fk_name = 'place_2'
    extra = 1


class ItemInline(admin.TabularInline):
    model = Item
    extra = 3


class InventoryInline(admin.TabularInline):
    model = Rucksack.contents.through
    extra = 1


class HeroAdmin(admin.ModelAdmin):
    inlines = [ClockInline, WalletInline, SituationInline]


class PlaceAdmin(admin.ModelAdmin):
    inlines = [LandmarkInline, Bridge1Inline, Bridge2Inline]


class ItemAdmin(admin.ModelAdmin):
    inlines = [InventoryInline]
    exclude = ['contents']


class RucksackAdmin(admin.ModelAdmin):
    inlines = [InventoryInline]


admin.site.register(Hero, HeroAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Rucksack, RucksackAdmin)
admin.site.register(Situation)
admin.site.register(Landmark)
