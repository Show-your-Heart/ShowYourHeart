from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from project.admin import ModelAdmin, gov_admin_site
from project.decorators import gov_admin_register, register_with_default_templates
from project.mixins import NetworkFilterMixin

from .forms import NetworkForm
from .models import LegalStructure, Network, Sector, SMTPServer


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=LegalStructure)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=LegalStructure)
class LegalStructureAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ("name",)
    search_fields = ["name"]
    autocomplete_fields = ["parent"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en", "parent"],
            translatable_fields=["name"],
        )


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Network)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Network)
class NetworkAdmin(ModelAdmin):
    form = NetworkForm
    search_fields = ["name"]
    list_display = ("name", "parent_network")
    filter_horizontal = ("organizations", "methods", "campaigns")
    autocomplete_fields = ["parent_network"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=[
                "name",
                "parent_network",
                "organizations",
                "campaigns",
                "methods",
            ],
            translatable_fields=None,
        )


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=Sector)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=Sector)
class SectorAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ("name",)
    search_fields = ["name"]

    def get_fieldsets(self, request, obj=None):
        return self.build_fieldsets(
            main_fields=["name_en"],
            translatable_fields=["name"],
        )


# Add superadmin views with default Unfold templates
@register_with_default_templates(admin.site, model=SMTPServer)
# Add admin views with custom templates
@gov_admin_register(gov_admin_site, model=SMTPServer)
class SMTPServerAdmin(NetworkFilterMixin, ModelAdmin):
    list_display = ("network", "host", "port", "protocol", "username", "password")
