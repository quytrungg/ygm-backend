from django.db import models
from django.utils.translation import gettext_lazy as _

from safedelete.config import SOFT_DELETE

from apps.core.models import BaseModel


class TimelineCategory(BaseModel):
    """Represent category of timeline in DB.

    Attributes:
        - name: category's name of timeline

    """

    _safedelete_policy = SOFT_DELETE

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )

    class Meta:
        verbose_name = _("Timeline Category")
        verbose_name_plural = _("Timeline Categories")

    def __str__(self) -> str:
        return self.name
