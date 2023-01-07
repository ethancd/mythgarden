from django.contrib import admin

from .models import Quandary, Answer

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3

class QuandaryAdmin(admin.ModelAdmin):
    fields = ['quandary_text', 'description']
    inlines = [AnswerInline]
    list_display = ['quandary_text', 'has_description']
    list_filter = ['created_at']
    search_fields = ['quandary_text']


admin.site.register(Quandary, QuandaryAdmin)
admin.site.register(Answer)
