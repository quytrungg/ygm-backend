from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseMedia
from apps.resources.constants import FileTypes
from apps.users.constants import UserRole


class Resource(BaseMedia):
    """Represent resources in DB which store files.

    Attributes:
        - id: unique id of a resource
        - name: resource name
        - resource_url: attached url which belongs to a resource
        - resource_category: foreign key to a resource category

    """

    category = models.ForeignKey(
        to="resources.ResourceCategory",
        verbose_name=_("Resource Category ID"),
        related_name="resources",
        on_delete=models.CASCADE,
    )
    user_group = ArrayField(
        base_field=models.CharField(
            choices=UserRole.choices,
            default=UserRole.CHAMBER_ADMIN,
            max_length=255,
        ),
    )
    file_type = models.CharField(
        choices=FileTypes.choices,
        default=FileTypes.PDF.value,
        max_length=255,
    )
    external_id = models.IntegerField(
        verbose_name=_("ID from old db"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Resource")
        verbose_name_plural = _("Resources")

    def __str__(self) -> str:
        return self.name
