from django.db import models
from django.utils.translation import gettext_lazy as _

from project.models import BaseModel


class Organization(BaseModel):
    class Status(models.IntegerChoices):
        PENDING = (
            0,
            "Pending",
        )
        ACCEPTED = (
            1,
            "Accepted",
        )
        REJECTED = 2, "Rejected"

    name = models.CharField(_("name"), max_length=50)
    vat_number = models.CharField(_("vat number"), max_length=20)
    contact = models.ForeignKey("users.User", on_delete=models.CASCADE)
    website = models.CharField(_("website"), max_length=100, blank=True, default="")
    country = models.CharField(_("country"), max_length=50)
    region = models.CharField(_("region"), max_length=50)
    city = models.CharField(_("city"), max_length=50)
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.PENDING
    )
    legal_structure = models.ForeignKey(
        "settings.LegalStructure",
        on_delete=models.CASCADE,
        related_name="legal_structure",
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/organizations/sign-up"
