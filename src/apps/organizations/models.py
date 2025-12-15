from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.users.models import UserProfile
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

    name = models.CharField(_("name"), max_length=150)
    logo = models.FileField(upload_to="logos/", null=True, blank=True)
    vat_number = models.CharField(_("vat number"), max_length=30)
    website = models.CharField(_("website"), max_length=300, blank=True, default="")
    country = models.ForeignKey(
        "geodata.country", on_delete=models.CASCADE, blank=True, null=True
    )
    region3 = models.ForeignKey(
        "geodata.region3", on_delete=models.CASCADE, blank=True, null=True
    )
    city = models.ForeignKey(
        "geodata.city", on_delete=models.CASCADE, blank=True, null=True
    )
    address = models.CharField(_("address"), max_length=100, blank=True)
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
    privacy_policy_accepted = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/organizations/sign-up"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == Organization.Status.ACCEPTED:
            profile = UserProfile.objects.filter(organization=self).first()
            if profile and not profile.user.email_verified:
                send_welcome_mail(profile.user)


class Project(BaseModel):
    class ActionScope(models.TextChoices):
        COMMUNITY_ACTION = "CA", _("Community action")
        SOCIAL_COHESION = "SC", _("Social cohesion")
        CULTURE = "CULT", _("Culture")
        SPORTS = "SP", _("Sports")
        CHILDHOOD = "CH", _("Childhood")
        YOUTH = "Y", _("Youth")
        ELDERLY = "ELD", _("Elderly")
        WOMEN_FEMINISM = "WF", _("Women - Feminism")
        LGTBI = "LGTBI", _("LGTBI")
        HEALTH = "H", _("Health")
        INTERCULTURALITY = "INT", _("Interculturality")
        FUNCTIONAL_DIVERSITY = "FD", _("Funcional diversity")
        ENVIRONMENTAL_SUSTAINABILITY = "ES", _("Environmental sustainability")
        SOCIAL_ECONOMY = "SE", _("Social and solidarity economy")
        COMMERCE = "C", _("Commerce")
        URBAN_PLANNING = "UP", _("Urban planning")
        INTERNATIONAL_COOPERATION = "IC", _("International cooperation")
        LEISURE_EDUCATION = "LE", _("Leisure education and educational services")
        RESEARCH_NEW_TECH = "RNT", _("Research and new technologies")
        NETWORKS_ENTITY_SUPPORT = "NSE", _("Networks and support for entities")
        OTHER = "O", _("Other")

    class LegalEntityType(models.TextChoices):
        NEIGHBORHOOD = "N", _("Neighborhood")
        DISTRICT = "D", _("District")
        CITY = "CM", _("City/Municipality")
        COUNTY = "C", _("County")

    organization = models.ForeignKey(
        "organizations.organization",
        related_name="projects",
        on_delete=models.CASCADE,
    )
    vat_number = models.CharField(_("vat number"), max_length=30)
    name = models.CharField(_("name"), max_length=150)
    description = models.CharField(_("description"), blank=True, max_length=400)
    contact_name = models.CharField(_("contact person"), blank=True, max_length=150)
    contact_email = models.CharField(_("contact email"), blank=True, max_length=255)
    contact_telephone = models.CharField(
        _("contact telephone"), blank=True, max_length=20
    )
    city = models.ForeignKey(
        "geodata.city", on_delete=models.CASCADE, blank=True, null=True
    )
    region3 = models.ForeignKey(
        "geodata.region3", on_delete=models.CASCADE, blank=True, null=True
    )
    main_action_scope = models.CharField(
        _("main scope of action"),
        choices=ActionScope.choices,
        default=ActionScope.COMMUNITY_ACTION,
        blank=False,
    )
    secondary_action_scope = models.CharField(
        _("secondary fields of action"),
        choices=ActionScope.choices,
        default="",
        blank=True,
    )
    main_legal_entity_type = models.CharField(
        _("Main legal entity type"),
        choices=LegalEntityType.choices,
        default=LegalEntityType.NEIGHBORHOOD,
        blank=False,
    )
    secondary_legal_entity_type = models.CharField(
        _("Secondary legal entity type"),
        choices=LegalEntityType.choices,
        default=LegalEntityType.NEIGHBORHOOD,
        blank=False,
    )
    methods = models.ManyToManyField(
        "methods.Method",
        verbose_name=_("Methods"),
        related_name="project_methods",
        blank=True,
    )
    start_date = models.DateField(_("Start date"), blank=True, null=True)
    end_date = models.DateField(_("End date"), blank=True, null=True)
    publish_results = models.BooleanField(
        _("I want to make public the results"), max_length=50, blank=True, null=True
    )
    authorize = models.BooleanField(
        _("Authorize the use of my data for inclusion in the final report"),
        max_length=50,
    )
    bs_allow_public = models.BooleanField(
        _("Allow infographics to be public"), blank=True, null=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.vat_number = self.organization.vat_number
        self.city = self.organization.city
        self.region3 = self.organization.region3
