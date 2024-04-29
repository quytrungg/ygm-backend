from django.db import models
from django.utils.translation import gettext_lazy as _

import safedelete

from apps.core.constants import MAX_PHONE_NUMBER_LENGTH
from apps.core.models import BaseModel


class StoredMemberContact(BaseModel):
    """Represent contact information of a stored member."""

    _safedelete_policy = safedelete.HARD_DELETE

    stored_member = models.ForeignKey(
        verbose_name=_("Stored Member"),
        to="chambers.StoredMember",
        related_name="contacts",
        on_delete=models.CASCADE,
    )
    first_name = models.CharField(
        verbose_name=_("Contact First Name"),
        max_length=255,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name=_("Last Name"),
        max_length=255,
        blank=True,
    )
    email = models.EmailField(
        verbose_name=_("Email"),
        max_length=255,
    )
    work_phone = models.CharField(
        verbose_name=_("Work Phone"),
        max_length=MAX_PHONE_NUMBER_LENGTH,
        blank=True,
    )
    mobile_phone = models.CharField(
        verbose_name=_("Mobile Phone"),
        max_length=MAX_PHONE_NUMBER_LENGTH,
        blank=True,
    )
    external_id = models.IntegerField(
        verbose_name=_("ID in old DB"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Stored Member Contact")
        verbose_name_plural = _("Stored Member Contacts")

    def __str__(self) -> str:
        return f"{self.email} - Member {self.stored_member_id}"
