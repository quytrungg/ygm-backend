from django.db import models
from django.utils.translation import gettext_lazy as _

from safedelete.config import SOFT_DELETE

from apps.core.models import BaseModel
from apps.timelines.constants import TimelineTypeChoice


class TimelineType(BaseModel):
    """Represent type of timeline in DB: `23OS TC` and `23OS VC`."""

    _safedelete_policy = SOFT_DELETE

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        choices=TimelineTypeChoice.choices,
        unique=True,
    )

    class Meta:
        verbose_name = _("Timeline Type")
        verbose_name_plural = _("Timeline Types")

    def __str__(self) -> str:
        return self.name
