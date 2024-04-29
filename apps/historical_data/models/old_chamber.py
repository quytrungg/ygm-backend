from django.db import models
from django.utils.translation import gettext_lazy as _

import safedelete

from apps.core.models import BaseModel


class OldChamber(BaseModel):
    """Represent a chamber in legacy app."""

    _safedelete_policy = safedelete.HARD_DELETE

    id = models.IntegerField(
        verbose_name=_("Id"),
        primary_key=True,
    )
    name = models.CharField(
        max_length=50,
    )
    description = models.CharField(
        max_length=255,
    )
    old_id = models.IntegerField(
        verbose_name=_("Original Chamber Id"),
        help_text=_("Chamber from which current chamber is duplicated"),
        null=True,
        blank=True,
    )
    originally_created = models.DateField(null=True)

    class Meta:
        verbose_name = _("Old Chamber")
        verbose_name_plural = _("Old Chambers")

    def __str__(self) -> str:
        return self.name
