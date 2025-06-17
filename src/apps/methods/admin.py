from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from project.admin import ModelAdmin

from .models import Indicator, Method, Topic


class TopicAdmin(ModelAdmin, TranslationAdmin):
    search_fields = ["name"]

    list_display = (
        "name",
        "description",
        "parent",
    )

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en", "description_en", "parent"],
            translatable_fields=["name", "description"],
            display_log=False,
        )


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

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=[
                "project_id",
                "version",
                "name_en",
                "description_en",
                "is_direct_indicator",
                "topics",
                "category",
                "data_type",
                "unit",
                "list_options",
                "condition",
                "formula",
                "validation",
                "message",
            ],
            translatable_fields=["name", "description"],
            display_log=False,
        )


class MethodAdmin(ModelAdmin, TranslationAdmin):
    autocomplete_fields = ["network_owner"]
    search_fields = ["name"]

    list_display = (
        "name",
        "description",
        "active",
        "network_owner",
    )

    conditional_fields = {
        "external_surveys": f"unit_of_analysis != '{Method.UnitAnalysis.EXTERNAL_SURVEY}'",
    }

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.network_owner = obj.network_owner
            return super().get_form(request, obj, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # External surveys field must only display
        # methods for the same network and set as external survey
        if (db_field.name == "external_surveys") & hasattr(self, "network_owner"):
            kwargs["queryset"] = Method.objects.filter(
                network_owner=self.network_owner,
                unit_of_analysis=Method.UnitAnalysis.EXTERNAL_SURVEY,
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=[
                "name_en",
                "description_en",
                "active",
                "network_owner",
                "unit_of_analysis",
                "indicators",
                "related_legal_structures",
                "external_surveys",
            ],
            translatable_fields=["name", "description"],
        )


admin.site.register(Method, MethodAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Indicator, IndicatorAdmin)
