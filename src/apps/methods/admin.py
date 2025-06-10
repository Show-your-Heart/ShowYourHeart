from django.conf import settings
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from project.admin import ModelAdmin

from .models import Indicator, Topic


class TopicAdmin(ModelAdmin, TranslationAdmin):
    search_fields = ["name"]

    list_display = (
        "name",
        "description",
        "parent",
    )

    fieldsets = [
        (
            (""),
            {
                "fields": (
                    "name",
                    "description",
                    "parent",
                )
            },
        ),
        (
            ("Log"),
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    ]

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
    autocomplete_fields = ["topics"]

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
    common_fieldsets = [
        (
            ("Log"),
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    ]

    def get_fieldsets(self, request, obj=None):
        # Do not display "log fields" twice, display them only on a "Log" section
        log_fields = [
            "created_by",
            "created_at",
            "updated_at",
        ]
        default_fields = super().get_fieldsets(request, obj)

        filtered_default_fields = [
            (
                None,
                {
                    "fields": [
                        f for f in default_fields[0][1]["fields"] if f not in log_fields
                    ]
                },
            )
        ]
        return filtered_default_fields + self.common_fieldsets


admin.site.register(Topic, TopicAdmin)
admin.site.register(Indicator, IndicatorAdmin)
