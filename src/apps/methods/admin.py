from django.conf import settings
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from unfold.admin import ModelAdmin

from .models import Indicator, Topic


class TopicAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name", "description", "parent")

    def get_fieldsets(self, request, obj=None):
        # Get all configured language codes except 'en'
        other_langs = [lang[0] for lang in settings.LANGUAGES if lang[0] != "en"]
        translatable_fields = [
            "name",
            "description",
        ]

        main_fields = ["name_en", "description_en", "parent"]
        other_fields = [
            f"{field}_{lang}" for field in translatable_fields for lang in other_langs
        ]

        return [
            (
                "Add/Edit Topic",
                {
                    "fields": main_fields,
                    "classes": ("tab",),
                },
            ),
            (
                "Translations",
                {
                    "fields": other_fields,
                    "classes": ("tab",),
                },
            ),
        ]


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
