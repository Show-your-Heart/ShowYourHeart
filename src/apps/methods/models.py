import re
import uuid

from django.core.exceptions import (
    MultipleObjectsReturned,
    ObjectDoesNotExist,
    ValidationError,
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from sortedm2m.fields import SortedManyToManyField

from project.models import BaseModel

from .utils import parse_expression_dependencies


class Topic(BaseModel):
    name = models.CharField(_("name"), max_length=100)
    description = models.CharField(_("description"), max_length=400)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if self.topics.exists():
            raise ValidationError(
                _("This topic is already used by indicators and cannot be deleted.")
            )
        super().delete(*args, **kwargs)


class ListItem(BaseModel):
    title = models.CharField(_("title"), max_length=300)
    formula = models.CharField(_("formula"), max_length=50, blank=True)
    value = models.PositiveSmallIntegerField(_("value"))

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        if self.items.exists():
            raise ValidationError(
                _(
                    "This list item has already been used and cannot be deleted. "
                    "Please create a new list item instead."
                )
            )
        super().delete(*args, **kwargs)


class List(BaseModel):
    title = models.CharField(_("title"), max_length=50)
    enable_others = models.BooleanField(
        _("Enable others response"), blank=False, default=False
    )
    items = SortedManyToManyField(ListItem, blank=True)

    def __str__(self):
        return self.title


class GroupItem(BaseModel):
    title = models.CharField(_("title"), max_length=300)
    suffix = models.CharField(_("suffix"), max_length=300, unique=True)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        if self.items.exists():
            raise ValidationError(
                _(
                    "This group item has already been used and cannot be deleted. "
                    "Please create a new group item instead."
                )
            )
        super().delete(*args, **kwargs)


class Group(BaseModel):
    title = models.CharField(_("title"), max_length=50)
    # enable_others = models.BooleanField(
    #     _("Enable others response"), blank=False, default=False
    # )
    items = SortedManyToManyField(GroupItem, blank=True)

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
        INTEGERGENDER = "IG", _("Integer gendered value")
        DECIMALGENDER = "DG", _("Real gendered number")

    class Unit(models.TextChoices):
        PEOPLE = "PE", _("people")
        DOLLAR = "DL", "$"
        EUROS = "EU", "€"
        KILO = "K", _("kg")
        M2 = "M", _("m2")
        TEMP = "T", _("°C")
        DAYS = "D", _("days")
        POINTS = "P", _("points")
        ENERGY = "E", _("KWh")
        EURO_HOUR = "EH", _("€/h")
        NUMBER = "N", _("number")
        PERCENTAGE = "PER", "%"

    list_types = [
        DataType.DROPDOWN,
        DataType.CHECKBOX,
        DataType.RADIOBUTTON,
    ]

    group_types = [
        DataType.STRING,
        DataType.INTEGER,
        DataType.DECIMAL,
    ]

    numeric_types = [
        DataType.INTEGER,
        DataType.DECIMAL,
    ]

    code = models.CharField(_("ID"), max_length=50, unique=True)
    version = models.CharField(_("version"), max_length=4)
    name = models.CharField(_("name"), max_length=1000, blank=True)
    description = models.CharField(_("description"), max_length=2500, blank=True)
    topics = models.ManyToManyField(Topic, related_name="topics")
    is_direct_indicator = models.BooleanField(
        _("Is it a direct indicator?"), blank=True
    )
    display_indirect = models.BooleanField(
        _("Display indirect indicator?"), blank=False, default=False
    )
    is_group_indicator = models.BooleanField(
        _("Is it a group indicator? (e.g. lists or tables)"), blank=False, default=False
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
    unit = models.CharField(  # noqa: DJ001
        _("unit"), choices=Unit.choices, default=None, blank=True, null=True
    )
    list_options = models.ForeignKey(
        List,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="list_options",
    )
    group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="group",
    )
    group_total = models.BooleanField(_("Add group total?"), blank=False, default=False)
    group_2 = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="group_2",
    )
    group_2_total = models.BooleanField(
        _("Add group totals?"), blank=False, default=False
    )
    condition = models.CharField(_("condition"), max_length=400, blank=True)
    formula = models.CharField(_("formula"), max_length=400, blank=True)
    validation = models.CharField(_("validation"), max_length=400, blank=True)
    dependant_indicators = models.JSONField(
        "dependant_indicators", blank=True, null=True
    )
    mandatory = models.BooleanField(_("Is it mandatory?"), blank=False, default=True)
    message = models.CharField(_("message"), max_length=400, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_condition = self.condition
        self.__original_validation = self.validation
        self.__original_formula = self.formula

    def __str__(self):
        return f"{self.code} - {self.name}"

    def delete(self, *args, **kwargs):
        if (
            self.indicators.exists()
            or self.indicatorresult_set.exists()
            or self.section_set.exists()
            or self.dependant_indicators
        ):
            raise ValidationError(
                _("This indicator has already been used and cannot be deleted.")
            )
        super().delete(*args, **kwargs)

    def clean(self):
        super().clean()

        if self.data_type in self.list_types and not self.list_options:
            raise ValidationError(
                {
                    "list_options": _(
                        "This field is required when data type "
                        + f"is {self.get_data_type_display()}."
                    )
                }
            )
        if not self.is_direct_indicator and not self.formula:
            raise ValidationError(
                {"formula": _("This field is required if the indicator is indirect.")}
            )

    def update_dependencies(self):
        # Get dependencies to add and dependencies to remove
        if (
            self.condition != self.__original_condition
            or self.validation != self.__original_validation
            or self.formula != self.__original_formula
        ):
            old_condition_deps = parse_expression_dependencies(
                self.__original_condition
            )
            old_validation_deps = parse_expression_dependencies(
                self.__original_validation
            )
            old_formula_deps = parse_expression_dependencies(self.__original_formula)
            old_deps = set().union(
                old_condition_deps, old_validation_deps, old_formula_deps
            )
            # remove self code
            old_deps = old_deps.difference([self.code])

            condition_deps = parse_expression_dependencies(self.condition)
            validation_deps = parse_expression_dependencies(self.validation)
            formula_deps = parse_expression_dependencies(self.formula)
            deps = set().union(condition_deps, validation_deps, formula_deps)
            # remove self code
            deps = deps.difference([self.code])

            deps_to_remove = list(old_deps.difference(deps))
            deps_to_add = list(deps.difference(old_deps))

            for code in deps_to_add:
                # avoid circular dependencies
                if self.dependant_indicators and code in self.dependant_indicators:
                    raise ValidationError({_("Circular dependencies")})
                    continue

                indicator = self.get_indicator(code)
                if indicator:
                    if indicator.dependant_indicators:
                        indicator.dependant_indicators.append(self.code)
                        indicator.save()
                    else:
                        indicator.dependant_indicators = [self.code]
                        indicator.save()

            for code in deps_to_remove:
                try:
                    indicator = self.get_indicator(code)
                except ValidationError:
                    pass

                if indicator:
                    if (
                        indicator.dependant_indicators
                        and self.code in indicator.dependant_indicators
                    ):
                        indicator.dependant_indicators.remove(self.code)
                        indicator.save()

    def get_indicator(self, code):
        indicator = None
        try:
            if "_" in code:
                subtoken = re.split(r"[_]", code)
                indicator = Indicator.objects.get(code=subtoken[0])
            else:
                indicator = Indicator.objects.get(code=code)
        except ObjectDoesNotExist:
            raise ValidationError(
                {_(f"Indicator with code {code} does not exist")}
            ) from ObjectDoesNotExist
        except MultipleObjectsReturned:
            raise ValidationError(
                {_(f"There are multiple indicators with code {code}")}
            ) from MultipleObjectsReturned

        return indicator

    def save(self, *args, **kwargs):
        self.update_dependencies()
        if "_" in self.code:
            raise ValidationError(
                {_("Indicator code can't contain the underscore character '_'")}
            )
        return super(Indicator, self).save(*args, **kwargs)


class IndicatorsSet(BaseModel):
    code = models.CharField(_("ID"), max_length=50, unique=True)
    version = models.CharField(_("version"), max_length=4)
    name = models.CharField(_("set name"), max_length=1000, blank=True)
    description = models.CharField(_("description"), max_length=2500, blank=True)
    instance_name = models.CharField(_("item name"), max_length=1000, blank=True)
    indicators = SortedManyToManyField(Indicator, related_name="sets")

    def __str__(self):
        return f"{self.code} - {self.name}"


class Method(BaseModel):
    class UnitAnalysis(models.TextChoices):
        ORGANIZATION = "ORG", _("Organisation")
        PROJECT = "PRO", _("Project")
        EXTERNAL_SURVEY = "EXT", _("External Survey")

    class ExternalSurveyCategory(models.TextChoices):
        WORK = "W", _("Work")
        PROFESSIONAL = "PR", _("Professional")
        ASSOCIATIVE = "AS", _("Associative")
        VOLUNTEERING = "V", _("Volunteering")

    name = models.CharField(_("name"), max_length=150)
    description = models.TextField(_("description"), max_length=1000)
    unit_of_analysis = models.CharField(
        _("unit of analysis"),
        choices=UnitAnalysis.choices,
        default=UnitAnalysis.ORGANIZATION,
        max_length=3,
        blank=False,
    )
    indicators = models.ManyToManyField(Indicator, related_name="methods")
    indicators_sets = models.ManyToManyField(
        IndicatorsSet, related_name="methods", null=True
    )
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
    version = models.CharField(_("Version"), max_length=400, blank=True)
    region1 = models.ManyToManyField(
        "geodata.region1",
        verbose_name=_("Region1"),
        related_name="region1",
        blank=False,
    )
    external_survey_category = models.CharField(
        _("external survey category"),
        choices=ExternalSurveyCategory.choices,
        default=ExternalSurveyCategory.WORK,
        blank=False,
    )

    def __str__(self):
        if self.version:
            networks_str = ", ".join([n.name for n in self.networks.all()])
            return f"{self.name}-{self.version} | {networks_str}"
        else:
            networks_str = ", ".join([n.name for n in self.networks.all()])
            return f"{self.name} | {networks_str}"

    def delete(self, *args, **kwargs):
        if (
            self.campaign_methods.exists()
            or self.survey_set.exists()
            or self.externalsurveyinvitation_set.exists()
            or self.section_set.exists()
        ):
            raise ValidationError(
                _("This method has already been used and cannot be deleted.")
            )
        super().delete(*args, **kwargs)


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
    )
    start_date = models.DateField(_("Start date"), blank=True, null=True)
    end_date = models.DateField(_("End date"), blank=True, null=True)

    def __str__(self):
        return self.year

    def delete(self, *args, **kwargs):
        if (
            self.survey_set.exists()
            or self.externalsurveyinvitation_set.exists()
            or self.campaign_set.exists()
        ):
            raise ValidationError(
                _("This campaign has already been used and cannot be deleted.")
            )
        super().delete(*args, **kwargs)


class Survey(BaseModel):
    class Status(models.IntegerChoices):
        OPEN = (
            0,
            "Open",
        )
        CLOSED = (
            1,
            "Closed",
        )
        TECH_VALIDATED = (
            2,
            "Tech validated",
        )
        QUALITY_CHECKED = (
            3,
            "Quality checked",
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
    organization = models.ForeignKey(
        "organizations.organization",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )
    project = models.ForeignKey(
        "organizations.project",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )
    start_date = models.DateTimeField(_("Start date"), blank=True, null=True)
    closed_date = models.DateTimeField(_("Closed date"), blank=True, null=True)
    modified_date = models.DateTimeField(_("Modified date"), blank=True, null=True)
    validated_date = models.DateTimeField(_("Validated date"), blank=True, null=True)
    evaluated_date = models.DateTimeField(_("Evaluated date"), blank=True, null=True)

    def __str__(self):
        return self.method.name + " | " + self.campaign.year


class IndicatorResult(BaseModel):
    class Gender(models.IntegerChoices):
        MALE = (
            0,
            "Male",
        )
        FEMALE = (
            1,
            "Female",
        )
        NON_BINARY = (2, "Non binary")

    survey = models.ForeignKey("methods.survey", on_delete=models.PROTECT)
    indicator = models.ForeignKey("methods.indicator", on_delete=models.PROTECT)
    group_item = models.ForeignKey(
        GroupItem,
        default=None,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="group_item",
    )
    group_2_item = models.ForeignKey(
        GroupItem,
        default=None,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="group_2_item",
    )
    gender = models.PositiveSmallIntegerField(
        choices=Gender.choices, default=None, blank=True, null=True
    )
    is_total = models.BooleanField(_("Is total?"), blank=False, default=False)
    instance_number = models.PositiveSmallIntegerField(
        _("Set instance number"), default=0, blank=False, null=False
    )
    value = models.CharField(blank=True)
    not_applicable = models.BooleanField(
        _("not applicable"), blank=True, null=True, default=None
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["survey", "indicator", "gender"], name="pk_indicator_result"
            )
        ]


class ExternalSurveyInvitation(BaseModel):
    name = models.CharField(_("Name"), max_length=400)
    external_survey = models.ForeignKey(
        "methods.Method",
        on_delete=models.PROTECT,
        limit_choices_to={"unit_of_analysis": Method.UnitAnalysis.EXTERNAL_SURVEY},
    )
    organization = models.ForeignKey(
        "organizations.organization",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
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
        REGISTERED = (
            3,
            "Registered",
        )

    class Gender(models.IntegerChoices):
        MALE = (
            0,
            "Male",
        )
        FEMALE = (
            1,
            "Female",
        )
        NON_BINARY = (2, "Non binary")

    name = models.CharField(_("Name"), max_length=400)
    surnames = models.CharField(_("Surnames"), max_length=400)
    email = models.EmailField(
        verbose_name=_("email address"),
        max_length=255,
    )
    gender = models.PositiveSmallIntegerField(
        choices=Gender.choices, default=None, blank=True, null=True
    )
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.PENDING
    )
    send_date = models.DateField(_("Send date"), blank=True, null=True)
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


class Section(BaseModel):
    title = models.CharField(_("Title"), max_length=60)
    description = models.CharField(
        _("Description"), max_length=2000, blank=True, default=""
    )
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    method = models.ForeignKey(Method, on_delete=models.PROTECT)
    order = models.PositiveIntegerField(_("order"), default=0, db_index=True)
    indicators = SortedManyToManyField(Indicator, blank=True)
    indicators_sets = SortedManyToManyField(
        IndicatorsSet, related_name="sections", blank=True
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        if self.parent:
            return self.parent.title + " - " + self.title
        else:
            return self.title
