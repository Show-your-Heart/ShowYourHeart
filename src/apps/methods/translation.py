from modeltranslation.translator import TranslationOptions, register

from .models import Indicator, Topic


@register(Topic)
class TopicTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Indicator)
class IndicatorTranslationOptions(TranslationOptions):
    fields = ("name", "description")
