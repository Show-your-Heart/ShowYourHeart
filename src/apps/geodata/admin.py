from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from project.admin import ModelAdmin

from .models import AutonomousCommunity, City, Country, Province, Region, ZipCode


class AutonomousCommunityAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name", "country")
    search_fields = ["name"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en", "country"],
            translatable_fields=["name"],
            display_log=False,
        )


admin.site.register(AutonomousCommunity, AutonomousCommunityAdmin)


class CityAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name", "province", "region")
    search_fields = ["name"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en", "province", "region"],
            translatable_fields=["name"],
            display_log=False,
        )


admin.site.register(City, CityAdmin)


class CountryAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name",)
    search_fields = ["name"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en"],
            translatable_fields=["name"],
            display_log=False,
        )


admin.site.register(Country, CountryAdmin)


class ProvinceAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name", "country", "community")
    search_fields = ["name"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en", "country", "community"],
            translatable_fields=["name"],
            display_log=False,
        )


admin.site.register(Province, ProvinceAdmin)


class RegionAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name", "community", "province")
    search_fields = ["name"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en", "community", "province"],
            translatable_fields=["name"],
            display_log=False,
        )


admin.site.register(Region, RegionAdmin)


class ZipCodeAdmin(ModelAdmin):
    list_display = ("code", "city")
    search_fields = ["code"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["code", "city"],
            display_log=False,
        )


admin.site.register(ZipCode, ZipCodeAdmin)
