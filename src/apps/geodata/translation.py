from modeltranslation.translator import TranslationOptions, register

from .models import AutonomousCommunity, City, Country, Province, Region


@register(AutonomousCommunity)
class AutonomousCommunityTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(City)
class CityTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Country)
class CountryTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Province)
class ProvinceTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Region)
class RegionTranslationOptions(TranslationOptions):
    fields = ("name",)
