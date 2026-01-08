from django.db import models
from django.utils.translation import gettext as _

from project.models import BaseModel


class Country(BaseModel):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = _("countries")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Region1(BaseModel):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="region1_country",
    )

    class Meta:
        verbose_name_plural = _("regions (1)")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Region2(BaseModel):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="region2_country",
    )
    region1 = models.ForeignKey(
        Region1,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="region2_region1",
    )

    class Meta:
        verbose_name_plural = _("regions (2)")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Region3(BaseModel):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="region3_country",
    )
    region1 = models.ForeignKey(
        Region1,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="region3_region1",
    )
    region2 = models.ForeignKey(
        Region2,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="region3_region2",
    )

    class Meta:
        verbose_name_plural = _("regions (3)")
        ordering = ["name"]

    def __str__(self):
        return self.name


class City(BaseModel):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="city_country",
    )
    region2 = models.ForeignKey(
        Region2,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="city_region2",
    )
    region3 = models.ForeignKey(
        Region3,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="city_region3",
    )

    class Meta:
        verbose_name_plural = _("cities")
        ordering = ["name"]

    def __str__(self):
        return self.name


class ZipCode(BaseModel):
    code = models.CharField(max_length=10)
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="zip_code_city",
    )

    class Meta:
        verbose_name_plural = _("zip codes")
        ordering = ["code"]

    def __str__(self):
        return self.code
