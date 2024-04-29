from django.db import models
from django.utils.translation import gettext_lazy as _

from ordered_model.models import OrderedModel, OrderedModelManager
from safedelete.config import SOFT_DELETE
from safedelete.managers import (
    SafeDeleteAllManager,
    SafeDeleteDeletedManager,
    SafeDeleteManager,
)

from apps.core.models import BaseModel

from ..constants import TimelineStatus
from ..querysets import TimelineQuerySet


class TimelineManager(SafeDeleteManager, OrderedModelManager):
    """Provide custom manager for Timeline model."""


class TimelineAllManager(SafeDeleteAllManager, OrderedModelManager):
    """Provide custom all manager for Timeline model."""


class TimelineDeletedManager(SafeDeleteDeletedManager, OrderedModelManager):
    """Provide custom deleted manager for Timeline model."""


class Timeline(OrderedModel, BaseModel):
    """Represent a task/timeline in DB.

    Attributes:
        - name: task/timeline name
        - description: task/timeline description
        - due_date: due date of the task/timeline
        - status: status of the task/timeline
        - category: category of timeline
        - created_by: user who created the task/timeline
        - assigned_to: user whom is assigned to the task/timeline
        - chamber: chamber id that timeline belongs to

    """

    _safedelete_policy = SOFT_DELETE

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
    )
    due_date = models.DateTimeField(
        verbose_name=_("Due Date"),
        null=True,
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=255,
        choices=TimelineStatus.choices,
        default=TimelineStatus.NOT_STARTED,
    )
    category = models.ForeignKey(
        to="timelines.TimelineCategory",
        on_delete=models.CASCADE,
        verbose_name=_("Category"),
        related_name="timelines",
    )
    type = models.ForeignKey(
        to="timelines.TimelineType",
        on_delete=models.SET_NULL,
        verbose_name=_("Type"),
        related_name="timelines",
        null=True,
    )
    created_by = models.ForeignKey(
        to="users.User",
        on_delete=models.CASCADE,
        verbose_name=_("Created By"),
        related_name="created_timelines",
    )
    assigned_to = models.CharField(
        verbose_name=_("Assigned To"),
        max_length=255,
        blank=True,
    )
    chamber = models.ForeignKey(
        to="chambers.Chamber",
        on_delete=models.CASCADE,
        verbose_name=_("Chamber"),
        related_name="timelines",
    )

    order_with_respect_to = ("chamber", "type")
    objects = TimelineManager(queryset_class=TimelineQuerySet)
    all_objects = TimelineAllManager(queryset_class=TimelineQuerySet)
    deleted_objects = TimelineDeletedManager(queryset_class=TimelineQuerySet)

    class Meta(OrderedModel.Meta):
        verbose_name = _("Timeline")
        verbose_name_plural = _("Timelines")

    def __str__(self) -> str:
        return f"Timeline {self.name} from Chamber {self.chamber}"

    # pylint: disable=attribute-defined-outside-init
    def delete(self, *args, extra_update=None, **kwargs):
        """Overwrite delete method to return data after delete.

        OrderedModel's delete method returns None when delete objects, causing
        error when parent object (Camapaign is parent of ProductCategory) is
        deleted along with the related/children objects.

        See safedelete/models.py at line 237.

        """
        self._was_deleted_via_delete_method = True

        qs = self.get_ordering_queryset()
        extra_update = {} if extra_update is None else extra_update
        qs.above_instance(self).decrease_order(**extra_update)
        return super(BaseModel, self).delete(*args, **kwargs)

    def mark_completed(self) -> None:
        """Mark timeline as completed."""
        self.status = TimelineStatus.COMPLETED
        self.save()
