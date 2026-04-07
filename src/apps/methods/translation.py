from modeltranslation.translator import TranslationOptions, register

from .models import (
    Campaign,
    Group,
    GroupItem,
    Indicator,
    IndicatorsSet,
    List,
    ListItem,
    Method,
    Section,
    Topic,
)


@register(Topic)
class TopicTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Indicator)
class IndicatorTranslationOptions(TranslationOptions):
    fields = ("name", "description", "message")


@register(IndicatorsSet)
class IndicatorsSetTranslationOptions(TranslationOptions):
    fields = ("name", "description", "instance_name")


@register(Method)
class MethodTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Group)
class GroupTranslationOptions(TranslationOptions):
    fields = ("title",)


@register(GroupItem)
class GroupItemTranslationOptions(TranslationOptions):
    fields = ("title",)


@register(ListItem)
class ListItemTranslationOptions(TranslationOptions):
    fields = ("title",)


@register(List)
class ListTranslationOptions(TranslationOptions):
    fields = ("title",)


@register(Campaign)
class CampaignTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Section)
class SectionTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "description",
    )
