from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseMedia


class TimelineAttachment(BaseMedia):
    """Represent media resource for timeline.

    Attributes:
        - name: tasks media name
        - file: media file of task
        - content_type: media file type
        - timeline: timeline id that resource belongs to

    """

    content_type = models.CharField(
        verbose_name=_("Content Type"),
        max_length=255,
    )
    timeline = models.ForeignKey(
        to="timelines.Timeline",
        on_delete=models.CASCADE,
        verbose_name=_("Timeline"),
        related_name="attachments",
    )

    class Meta:
        verbose_name = _("Timeline Attachment")
        verbose_name_plural = _("Timeline Attachments")

    def __str__(self) -> str:
        return self.name
