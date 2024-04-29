from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class ResourceCategory(BaseModel):
    """Represent resource categories in DB.

    Categories group resources by type, owner or other
    grouping criteria.

    Attributes:
        - id: unique id of a resource category
        - name: name of a resource category

    """

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    chamber = models.ForeignKey(
        to="chambers.Chamber",
        verbose_name=_("Chamber"),
        related_name="resources",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Resource Category")
        verbose_name_plural = _("Resource Categories")

    def __str__(self) -> str:
        return self.name
