import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from project.models import BaseModel


class Topic(BaseModel):
    name = models.CharField(_("name"), max_length=50)
    description = models.CharField(_("description"), max_length=400)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.name


class ListItem(BaseModel):
    title = models.CharField(_("title"), max_length=50)
    formula = models.CharField(_("formula"), max_length=50)
    value = models.PositiveSmallIntegerField(_("value"))
    active = models.BooleanField(_("active"), max_length=50)

    def __str__(self):
        return self.title


class List(BaseModel):
    title = models.CharField(_("title"), max_length=50)
    enable_others = models.BooleanField(
        _("Enable others response"), blank=False, default=False
    )
    items = models.ManyToManyField(ListItem, related_name="items")

    def __str__(self):
        return self.title


class Indicator(BaseModel):
    class Category(models.TextChoices):
        PERFORMANCE = "PERF", _("Performance")
        SCORING = "SC", _("Scoring")
        CERTIFICATION = "CERT", _("Certification")

    class DataType(models.TextChoices):
        STRING = "S", _("String")
        TEXT = "T", _("Text")
        INTEGER = "I", _("Integer")
        DECIMAL = "DC", _("Decimal")
        BOOLEAN = "B", _("Boolean")
        DATE = "D", _("Date")
        ATTACHMENT = "A", _("Attachment")
        CHECKBOX = "CH", _("Checkbox")
        RADIOBUTTON = "R", _("Radiobutton")
        DROPDOWN = "DR", _("Dropdown")

    class SubDataType(models.TextChoices):
        INTEGERGENDER = "IG", _("Integer gendered value")
        DECIMALGENDER = "DG", _("Real gendered number")

    class Unit(models.TextChoices):
        C = "C", "C"
        DOLLAR = "DL", "$"
        KILO = "K", _("kg")
        M2 = "M", _("m2")
        TEMP = "T", _("°C")
        DAYS = "D", _("days")
        POINTS = "P", _("points")
        ENERGY = "E", _("KWh")

    project_id = models.CharField(_("ID"), max_length=50)
    version = models.CharField(_("version"), max_length=4)
    name = models.CharField(_("name"), max_length=50, blank=True)
    description = models.CharField(_("description"), max_length=400, blank=True)
    topics = models.ManyToManyField(Topic, related_name="topics")
    is_direct_indicator = models.BooleanField(
        _("Is it a direct indicator?"), blank=True
    )
    category = models.CharField(
        _("category"),
        choices=Category.choices,
        default=Category.PERFORMANCE,
        blank=True,
    )
    data_type = models.CharField(
        _("data type"), choices=DataType.choices, default=DataType.STRING
    )
    sub_data_type = models.CharField(
        _("sub data type"),
        choices=SubDataType.choices,
        default=SubDataType.INTEGERGENDER,
    )
    unit = models.CharField(_("unit"), choices=Unit.choices, default=Unit.KILO)
    list_options = models.ForeignKey(
        List,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="list_options",
    )
    condition = models.CharField(_("condition"), max_length=400, blank=True)
    formula = models.CharField(_("formula"), max_length=400, blank=True)
    validation = models.CharField(_("validation"), max_length=50, blank=True)
    message = models.CharField(_("message"), max_length=400, blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.data_type == Indicator.DataType.DROPDOWN and not self.list_options:
            raise ValidationError(
                {
                    "list_options": _(
                        "This field is required when data type is Dropdown."
                    )
                }
            )
        if not self.is_direct_indicator and not self.formula:
            raise ValidationError(
                {"formula": _("This field is required if the indicator is indirect.")}
            )


class Method(BaseModel):
    class UnitAnalysis(models.TextChoices):
        ORGANIZATION = "ORG", _("Organization")
        PROJECT = "PRO", _("Project")
        EXTERNAL_SURVEY = "EXT", _("External Survey")

    active = models.BooleanField(_("active"))
    name = models.CharField(_("name"), max_length=50)
    description = models.CharField(_("description"), max_length=400)
    network_owner = models.ForeignKey("settings.network", on_delete=models.PROTECT)
    unit_of_analysis = models.CharField(
        _("unit of analysis"),
        choices=UnitAnalysis.choices,
        default=UnitAnalysis.ORGANIZATION,
        max_length=3,
        blank=False,
    )
    indicators = models.ManyToManyField(Indicator, related_name="indicators")
    legal_structures = models.ManyToManyField(
        "settings.LegalStructure",
        verbose_name=_("Which entity does this method applies to?"),
        related_name="structures",
        blank=True,
    )
    sectors = models.ManyToManyField(
        "settings.Sector",
        verbose_name=_("Sectors"),
        related_name="sectors",
        blank=True,
    )
    external_surveys = models.ManyToManyField(
        "self",
        verbose_name=_("External surveys"),
        blank=True,
    )
    documentation = models.FileField(upload_to="documentation/", null=True, blank=True)

    def __str__(self):
        return self.name + " | " + self.network_owner.name


class Campaign(BaseModel):
    name = models.CharField(_("Name"), max_length=400, blank=True)
    year = models.CharField(_("Year"), max_length=4)
    status = models.BooleanField(_("Active"), blank=True)
    previous_campaign = models.ForeignKey(
        "self", on_delete=models.PROTECT, blank=True, null=True
    )
    methods = models.ManyToManyField(
        "methods.method",
        verbose_name=_("Methods"),
        related_name="campaign_methods",
        blank=True,
        limit_choices_to=~Q(unit_of_analysis=Method.UnitAnalysis.EXTERNAL_SURVEY),
    )
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"))

    def __str__(self):
        return self.year


class Survey(BaseModel):
    class Status(models.IntegerChoices):
        OPEN = (
            0,
            "Open",
        )
        SUBMITTED = (
            1,
            "Submitted",
        )

    method = models.ForeignKey("methods.method", on_delete=models.PROTECT)
    user = models.ForeignKey(
        "users.user", on_delete=models.PROTECT, blank=True, null=True
    )
    token = models.CharField(_("Token"), max_length=32, blank=True)
    campaign = models.ForeignKey("methods.campaign", on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.OPEN
    )

    def __str__(self):
        return self.method.name + " | " + self.campaign.year


class IndicatorResult(BaseModel):
    survey = models.ForeignKey("methods.survey", on_delete=models.PROTECT)
    indicator = models.ForeignKey("methods.indicator", on_delete=models.PROTECT)
    value = models.CharField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["survey", "indicator"], name="pk_indicator_result"
            )
        ]


class ExternalSurveyInvitation(BaseModel):
    name = models.CharField(_("Name"), max_length=400)
    external_survey = models.ForeignKey(
        "methods.Method",
        on_delete=models.PROTECT,
        limit_choices_to={"unit_of_analysis": Method.UnitAnalysis.EXTERNAL_SURVEY},
    )
    campaign = models.ForeignKey("methods.campaign", on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Invitation(BaseModel):
    class Status(models.IntegerChoices):
        PENDING = (
            0,
            "Pending",
        )
        SENT = (
            1,
            "Sent",
        )
        FILLED = (
            2,
            "Filled",
        )

    name = models.CharField(_("Name"), max_length=400)
    email = models.EmailField(
        verbose_name=_("email address"),
        max_length=255,
    )
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.PENDING
    )
    token = models.CharField(max_length=32, unique=True, blank=True)
    external_survey_invitation = models.ForeignKey(
        ExternalSurveyInvitation, on_delete=models.CASCADE, related_name="invitation"
    )

    def __str__(self):
        return self.name + " " + self.email

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email", "external_survey_invitation"], name="pk_invitation"
            )
        ]
