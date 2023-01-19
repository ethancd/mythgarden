from django.contrib import admin

from .models import Hero, Rucksack, Clock, Wallet, Situation, Place


class RucksackInline(admin.TabularInline):
    model = Rucksack
    max_num = 1


class ClockInline(admin.TabularInline):
    model = Clock
    max_num = 1


class WalletInline(admin.TabularInline):
    model = Wallet
    max_num = 1


class SituationInline(admin.TabularInline):
    model = Situation
    max_num = 1


class HeroAdmin(admin.ModelAdmin):
    inlines = [ClockInline, WalletInline, SituationInline, RucksackInline]


admin.site.register(Hero, HeroAdmin)
admin.site.register(Place)
