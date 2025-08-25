from modeltranslation.translator import TranslationOptions, register

from .models import Campaign, Indicator, List, ListItem, Method, Topic


@register(Topic)
class TopicTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Indicator)
class IndicatorTranslationOptions(TranslationOptions):
    fields = ("name", "description", "message")


@register(Method)
class MethodTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(ListItem)
class ListItemTranslationOptions(TranslationOptions):
    fields = ("title",)


@register(List)
class ListTranslationOptions(TranslationOptions):
    fields = ("title",)


@register(Campaign)
class CampaignTranslationOptions(TranslationOptions):
    fields = ("name",)
