from django.contrib import admin

from .models import Quandary, Answer, Landscape


class AnswerInline(admin.TabularInline):
    model = Answer
    fk_name = 'quandary'
    extra = 3


class ParentAnswerInline(admin.TabularInline):
    model = Answer
    fk_name = 'child_quandary'
    max_num = 1
    verbose_name = 'Parent Answer'

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class QuandaryAdmin(admin.ModelAdmin):
    fields = ['quandary_text', 'landscape']
    inlines = [ParentAnswerInline, AnswerInline]
    list_display = ['quandary_text']
    list_filter = ['created_at']
    search_fields = ['quandary_text']


admin.site.register(Quandary, QuandaryAdmin)
admin.site.register(Answer)
admin.site.register(Landscape)
