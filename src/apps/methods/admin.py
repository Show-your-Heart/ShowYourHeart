from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from unfold.admin import ModelAdmin

from .models import Indicator, Topic


class TopicAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name", "description", "parent")


class IndicatorAdmin(ModelAdmin, TranslationAdmin):
    list_display = (
        "project_id",
        "version",
        "name",
        "description",
    )


admin.site.register(Topic, TopicAdmin)
admin.site.register(Indicator, IndicatorAdmin)
