from modeltranslation.translator import TranslationOptions, register

from .models import LegalStructure, Sector


@register(LegalStructure)
class LegalStructureTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Sector)
class SectorTranslationOptions(TranslationOptions):
    fields = ("name",)
