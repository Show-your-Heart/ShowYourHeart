from django.db import models
from django.utils.translation import gettext_lazy as _

from project.models import BaseModel


class Topic(BaseModel):
    name = models.CharField(_("name"), max_length=50)
    description = models.CharField(_("description"), max_length=400)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.name

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

    class PreUnit(models.TextChoices):
        C = "C", "C"
        DOLLAR = "D", "$"

    class PostUnit(models.TextChoices):
        KILO = "K", _("kg")
        M2 = "M", _("m2")
        TEMP = "T", _("°C")
        DAYS = "D", _("days")
        POINTS = "P", _("points")
        ENERGY = "E", _("KWh")

    project_id = models.CharField(_("ID"), max_length=50)
    version = models.CharField(_("version"), max_length=4)
    name = models.CharField(_("name"), max_length=50)
    description = models.CharField(_("description"), max_length=400, blank=True)
    primary_topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="primary_topic")
    secondary_topics = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="secondary_topics")
    is_direct_indicator = models.BooleanField(_("Is it a direct indicator?"))
    category = models.CharField(_("category"), choices=Category.choices, default=Category.PERFORMANCE)
    data_type = models.CharField(_("data type"), choices=DataType.choices, default=DataType.STRING)
    pre_unit = models.CharField(_("pre unit"), choices=PreUnit.choices, default=PreUnit.DOLLAR)
    post_unit = models.CharField(_("post unit"), choices=PostUnit.choices, default=PostUnit.KILO)
    list_options = models.CharField(_("list options"), max_length=50)
    condition = models.CharField(_("condition"), max_length=400)
    formula = models.CharField(_("formula"), max_length=400)
    validation = models.CharField(_("validation"), max_length=50)
    message = models.CharField(_("message"), max_length=400)

    def __str__(self):
        return self.name
