from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.users.services import send_welcome_mail
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
        REJECTED = (
            2,
            "Rejected",
        )
        REGISTERED = (
            3,
            "Registered",
        )

    name = models.CharField(_("name"), max_length=150)
    vat_number = models.CharField(_("vat number"), max_length=30)
    contact = models.ForeignKey("users.User", on_delete=models.CASCADE)
    website = models.CharField(_("website"), max_length=300, blank=True, default="")
    country = models.ForeignKey(
        "geodata.country", on_delete=models.CASCADE, blank=True, null=True
    )
    region = models.ForeignKey(
        "geodata.region", on_delete=models.CASCADE, blank=True, null=True
    )
    city = models.ForeignKey(
        "geodata.city", on_delete=models.CASCADE, blank=True, null=True
    )
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.PENDING
    )
    legal_structure = models.ForeignKey(
        "settings.LegalStructure",
        on_delete=models.CASCADE,
        related_name="legal_structure",
    )
    methods = models.ManyToManyField(
        "methods.Method",
        verbose_name=_("Methods"),
        related_name="methods",
        blank=True,
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/organizations/sign-up"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if (
            self.status == Organization.Status.ACCEPTED
            and not self.contact.email_verified
        ):
            send_welcome_mail(self.contact)
