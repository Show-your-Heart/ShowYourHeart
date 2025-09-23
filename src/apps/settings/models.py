from django.db import models
from django.utils.translation import gettext_lazy as _

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
    network_admin = models.ForeignKey("users.User", on_delete=models.CASCADE)
    parent_network = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.RESTRICT
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Sector(BaseModel):
    name = models.CharField(_("name"), max_length=150)

    def __str__(self):
        return self.name
