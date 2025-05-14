from django.contrib import admin
from unfold.admin import ModelAdmin
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
        "is_direct_indicator",
    )
    conditional_fields = {
        "category": "is_direct_indicator == true",
        "condition": "is_direct_indicator == true",
        "formula": "is_direct_indicator == false",
    }


admin.site.register(Topic, TopicAdmin)
admin.site.register(Indicator, IndicatorAdmin)
