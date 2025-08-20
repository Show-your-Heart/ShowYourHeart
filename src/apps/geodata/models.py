from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class AutonomousCommunity(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="community_country",
    )

    class Meta:
        verbose_name_plural = "autonomous communities"

    def __str__(self):
        return self.name


class Province(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="province_country",
    )
    community = models.ForeignKey(
        AutonomousCommunity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="province_community",
    )

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=100)
    community = models.ForeignKey(
        AutonomousCommunity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="region_community",
    )
    province = models.ForeignKey(
        Province,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="region_province",
    )

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey(
        Province,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="city_province",
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="city_region",
    )

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self):
        return self.name


class ZipCode(models.Model):
    code = models.CharField(max_length=10)
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="zip_code_city",
    )

    def __str__(self):
        return self.code
