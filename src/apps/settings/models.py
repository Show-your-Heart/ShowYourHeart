from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.geodata.models import Region3
from apps.methods.models import Campaign, Indicator, Method
from project.models import BaseModel


class LegalStructure(BaseModel):
    name = models.CharField(_("name"), max_length=50)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.RESTRICT)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Network(BaseModel):
    name = models.CharField(_("name"), max_length=100)
    parent_network = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.RESTRICT
    )
    campaigns = models.ManyToManyField(Campaign, related_name="networks")
    methods = models.ManyToManyField(Method, related_name="networks")
    indicators = models.ManyToManyField(Indicator, related_name="networks")
    region3 = models.ForeignKey(
        Region3,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="networks",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Sector(BaseModel):
    name = models.CharField(_("name"), max_length=150)

    def __str__(self):
        return self.name
