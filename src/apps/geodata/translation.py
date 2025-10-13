from modeltranslation.translator import TranslationOptions, register

from .models import City, Country, Region1, Region2, Region3


@register(Region1)
class Region1TranslationOptions(TranslationOptions):
    fields = ("name",)


@register(City)
class CityTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Country)
class CountryTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Region2)
class Region2TranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Region3)
class Region3TranslationOptions(TranslationOptions):
    fields = ("name",)
