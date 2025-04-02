from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from project.admin import ModelAdmin

from .models import LegalStructure, Network, ParentNetwork


class LegalStructureAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name",)


admin.site.register(LegalStructure, LegalStructureAdmin)


@admin.register(ParentNetwork)
class ParentNetworkAdmin(ModelAdmin):
    list_display = ("name",)


@admin.register(Network)
class NetworkAdmin(ModelAdmin):
    list_display = ("name", "parent_network", "network_admin")
