from modeltranslation.translator import TranslationOptions, register

from .models import Indicator, Method, Topic


@register(Topic)
class TopicTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Indicator)
class IndicatorTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Method)
class MethodTranslationOptions(TranslationOptions):
    fields = ("name", "description")
