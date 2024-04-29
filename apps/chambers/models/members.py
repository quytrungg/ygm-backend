from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class StoredMember(BaseModel):
    """Members information within chamber."""

    chamber = models.ForeignKey(
        verbose_name=_("Chamber"),
        to="chambers.Chamber",
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name=_("Company Name"),
        max_length=255,
    )
    address = models.CharField(
        verbose_name=_("Company Address"),
        max_length=255,
        blank=True,
    )
    address2 = models.CharField(
        verbose_name=_("Company Address 2"),
        max_length=255,
        blank=True,
    )
    city = models.CharField(
        verbose_name=_("Company City"),
        max_length=255,
        blank=True,
    )
    state = models.CharField(
        verbose_name=_("Company State"),
        max_length=50,
        blank=True,
    )
    zip = models.CharField(
        verbose_name=_("Company Zip"),
        max_length=10,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\d{5}((-\d{1,4})|(\.0))?$",
                message=_("Invalid ZIP code"),
            ),
        ],
    )
    phone = models.CharField(
        verbose_name=_("Company Phone"),
        max_length=20,
        blank=True,
    )
    contact_first_name = models.CharField(
        verbose_name=_("Contact First Name"),
        max_length=255,
        blank=True,
    )
    contact_last_name = models.CharField(
        verbose_name=_("Contact Last Name"),
        max_length=255,
        blank=True,
    )
    contact_email = models.EmailField(
        verbose_name=_("Contact Email"),
        max_length=255,
        blank=True,
    )
    contact_work_phone = models.CharField(
        verbose_name=_("Contact Work Phone"),
        max_length=20,
        blank=True,
    )
    contact_mobile_phone = models.CharField(
        verbose_name=_("Contact Work Phone"),
        max_length=20,
        blank=True,
    )
    external_id = models.IntegerField(
        verbose_name=_("ID from old db"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Stored Member")
        verbose_name_plural = _("Stored Members")

    def __str__(self) -> str:
        return f"Stored Member for {self.chamber.name} - {self.name}"
