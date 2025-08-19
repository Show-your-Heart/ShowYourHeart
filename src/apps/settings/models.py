from django.db import models
from django.utils.translation import gettext_lazy as _

from project.models import BaseModel


class LegalStructure(BaseModel):
    name = models.CharField(_("name"), max_length=50)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.RESTRICT)

    def __str__(self):
        return self.name


class Network(BaseModel):
    name = models.CharField(_("name"), max_length=50)
    network_admin = models.ForeignKey("users.User", on_delete=models.CASCADE)
    parent_network = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.RESTRICT
    )

    def __str__(self):
        return self.name


class Sector(BaseModel):
    name = models.CharField(_("name"), max_length=50)

    def __str__(self):
        return self.name


class Gender(BaseModel):
    class GenderOptions(models.TextChoices):
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")
        NON_BINARY = "NB", _("Non Binary")

    name = models.CharField(
        _("name"),
        choices=GenderOptions.choices,
        default=GenderOptions.FEMALE,
        blank=False,
    )
