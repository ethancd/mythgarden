from django.contrib import admin

from .models import ScheduledEvent, Session, Hero, HeroState, Inventory, Clock, Wallet, Place, Building, Bridge, Item, PlaceState, Villager, VillagerState, ItemTypePreference


class ClockInline(admin.TabularInline):
    model = Clock
    max_num = 1


class WalletInline(admin.TabularInline):
    model = Wallet
    max_num = 1


class HeroInline(admin.TabularInline):
    model = HeroState
    max_num = 1


class BuildingInline(admin.TabularInline):
    model = Building
    fk_name = 'surround'
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
    model = Inventory
    max_num = 1


class SessionAdmin(admin.ModelAdmin):
    inlines = [HeroInline, ClockInline, WalletInline, InventoryInline]


class PlaceAdmin(admin.ModelAdmin):
    inlines = [BuildingInline, Bridge1Inline, Bridge2Inline]


class InventoryAdmin(admin.ModelAdmin):
    def save_related(self, request, obj, form, change):
        super().save_related(request, obj, form, change)
        obj.save()


admin.site.register(Session, SessionAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Item)
admin.site.register(Building)
admin.site.register(Clock)
admin.site.register(Wallet)
admin.site.register(HeroState)
admin.site.register(Hero)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(PlaceState)
admin.site.register(Villager)
admin.site.register(VillagerState)
admin.site.register(ItemTypePreference)
admin.site.register(ScheduledEvent)
