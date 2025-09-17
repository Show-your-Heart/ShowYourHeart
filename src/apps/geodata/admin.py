from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from project.admin import ModelAdmin, gov_admin_site
from project.decorators import gov_admin_register, register_with_default_templates

from .models import AutonomousCommunity, City, Country, Province, Region, ZipCode


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=AutonomousCommunity)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=AutonomousCommunity)
class AutonomousCommunityAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name", "country")
    search_fields = ["name"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en", "country"],
            translatable_fields=["name"],
            display_log=False,
        )


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=City)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=City)
class CityAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name", "province", "region")
    search_fields = ["name"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en", "province", "region"],
            translatable_fields=["name"],
            display_log=False,
        )


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Country)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Country)
class CountryAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name",)
    search_fields = ["name"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en"],
            translatable_fields=["name"],
            display_log=False,
        )


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Province)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Province)
class ProvinceAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name", "country", "autonomous_community")
    search_fields = ["name"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en", "country", "autonomous_community"],
            translatable_fields=["name"],
            display_log=False,
        )


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Region)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Region)
class RegionAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name", "autonomous_community", "province")
    search_fields = ["name"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en", "autonomous_community", "province"],
            translatable_fields=["name"],
            display_log=False,
        )


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=ZipCode)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=ZipCode)
class ZipCodeAdmin(ModelAdmin):
    list_display = ("code", "city")
    search_fields = ["code"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["code", "city"],
            display_log=False,
        )
