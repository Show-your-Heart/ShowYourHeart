from modeltranslation.translator import TranslationOptions, register

from .models import Topic
from .models import Indicator


@register(Topic)
class TopicTranslationOptions(TranslationOptions):
    fields = ("name", "description")

@register(Indicator)
class IndicatorTranslationOptions(TranslationOptions):
    fields = ("name", "description")
