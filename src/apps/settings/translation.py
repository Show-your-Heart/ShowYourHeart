from modeltranslation.translator import TranslationOptions, register

from .models import LegalStructure


@register(LegalStructure)
class LegalStructureTranslationOptions(TranslationOptions):
    fields = ("name",)
