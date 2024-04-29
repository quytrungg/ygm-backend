from django.db import models
from django.utils.translation import gettext_lazy as _

from ckeditor.fields import RichTextField

from apps.campaigns.constants import NoteType
from apps.campaigns.context_managers import get_context_manager
from apps.core.models import BaseModel


class Note(BaseModel):
    """Represent document templates within campaign."""

    type = models.CharField(
        verbose_name=_("Note Type"),
        max_length=255,
        choices=NoteType.choices,
    )
    body = RichTextField(
        verbose_name=_("Note text"),
    )
    campaign = models.ForeignKey(
        to="campaigns.Campaign",
        verbose_name=("Campaign ID"),
        related_name="notes",
        on_delete=models.CASCADE,
    )
    created_by = models.ForeignKey(
        to="users.User",
        verbose_name=_("Created by"),
        related_name="created_notes",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    modified_by = models.ForeignKey(
        to="users.User",
        verbose_name=_("Created by"),
        related_name="modified_notes",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")
        unique_together = ("campaign", "type")

    def __str__(self) -> str:
        """Return name of the instance."""
        return f"Note {self.campaign.name} - {self.type}"

    @property
    def context_variables(self) -> dict:
        """Return list of context variables."""
        return get_context_manager(self.type).get_context_info()
