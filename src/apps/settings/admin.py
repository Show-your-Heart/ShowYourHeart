from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from project.admin import ModelAdmin

from .models import LegalStructure


class LegalStructureAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name",)


admin.site.register(LegalStructure, LegalStructureAdmin)

