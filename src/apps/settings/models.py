from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.methods.models import Campaign, Method
from apps.organizations.models import Organization
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
    organizations = models.ManyToManyField(Organization, related_name="networks")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Sector(BaseModel):
    name = models.CharField(_("name"), max_length=150)

    def __str__(self):
        return self.name


class SMTPServer(BaseModel):
    class Protocol(models.TextChoices):
        TLS = "TLS", "TLS"
        SSL = "SSL", "SSL"

    network = models.OneToOneField(
        "settings.Network",
        on_delete=models.CASCADE,
        related_name="smtp_server",
        verbose_name=_("Network"),
    )
    host = models.CharField(_("Host"), max_length=255)
    port = models.PositiveIntegerField(_("Port"))
    username = models.CharField(_("Username"), max_length=255)
    password = models.CharField(_("Password"), max_length=255)
    protocol = models.CharField(_("Protocol"), choices=Protocol.choices, default="TLS")

    def __str__(self):
        return f"{self.network.name} SMTP"
