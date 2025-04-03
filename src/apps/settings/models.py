from django.db import models
from django.utils.translation import gettext_lazy as _

from project.models import BaseModel


class LegalStructure(BaseModel):
    name = models.CharField(_("name"), max_length=50)

    def __str__(self):
        return self.name
