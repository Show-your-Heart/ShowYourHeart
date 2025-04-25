from modeltranslation.translator import TranslationOptions, register

from .models import Topic


@register(Topic)
class TopicTranslationOptions(TranslationOptions):
    fields = ("name", "description")
