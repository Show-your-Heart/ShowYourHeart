from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from project.admin import ModelAdmin, gov_admin_site
from project.decorators import gov_admin_register, register_with_default_templates

from .models import City, Country, Region1, Region2, Region3, ZipCode


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Region1)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Region1)
class Region1Admin(ModelAdmin, TranslationAdmin):
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
    list_display = ("name", "region2", "region3", "country")
    search_fields = ["name"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en", "region2", "region3", "country"],
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
@register_with_default_templates(admin.site, model=Region2)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Region2)
class Region2Admin(ModelAdmin, TranslationAdmin):
    list_display = ("name", "country", "region1")
    search_fields = ["name"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en", "country", "region1"],
            translatable_fields=["name"],
            display_log=False,
        )


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Region3)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Region3)
class Region3Admin(ModelAdmin, TranslationAdmin):
    list_display = ("name", "region1", "region2")
    search_fields = ["name"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en", "region1", "region2"],
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
