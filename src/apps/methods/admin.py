from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from project.admin import ModelAdmin

from .forms import MethodForm
from .models import Campaign, Indicator, List, ListItem, Method, Topic


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
    autocomplete_fields = ["topics", "list_options"]

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
    form = MethodForm

    list_display = (
        "name",
        "description",
        "active",
        "network_owner",
    )

    conditional_fields = {
        "external_surveys": f"unit_of_analysis != '{Method.UnitAnalysis.EXTERNAL_SURVEY}'",  # noqa: E501
    }

    def get_form(self, request, obj=None, **kwargs):
        # Add network_owner property to use it on formfield_for_manytomany
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
                "sectors",
                "documentation",
                "external_surveys",
            ],
            translatable_fields=["name", "description"],
        )


admin.site.register(Method, MethodAdmin)


class ListAdmin(ModelAdmin, TranslationAdmin):
    autocomplete_fields = ["items"]
    search_fields = ["title"]

    list_display = ("title",)

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["title_en", "enable_others", "items"],
            translatable_fields=["title"],
        )


class ListItemAdmin(ModelAdmin, TranslationAdmin):
    search_fields = ["title"]

    list_display = (
        "title",
        "active",
    )

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["title_en", "formula", "value", "active"],
            translatable_fields=["title"],
        )


class CampaignAdmin(ModelAdmin):
    list_display = (
        "year",
        "name",
        "status",
    )


admin.site.register(Topic, TopicAdmin)
admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(List, ListAdmin)
admin.site.register(ListItem, ListItemAdmin)
admin.site.register(Campaign, CampaignAdmin)
