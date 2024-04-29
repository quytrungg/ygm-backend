import typing

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class Member(BaseModel):
    """Represent businesses/members in DB.

    Attributes:
    - name (str): name of the business.
    - title (str): title of the business.
    - address (str): address of the business.
    - city (str): city of the business.
    - state (str): state of the business. (2 characters)
    - zipcode (str): ZIP code of the business. (5 digits)
    - country (str): country of the business.
    - phone (str): phone number of the business.
    - fax (str): fax number of the business.
    - contact_methods (str): contact methods of the business.

    """

    stored_member = models.ForeignKey(
        to="chambers.StoredMember",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Stored member"),
    )
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    title = models.CharField(
        verbose_name=_("Title"),
        max_length=255,
    )
    representative = models.CharField(
        verbose_name=_("Representative"),
        max_length=255,
    )
    address = models.CharField(
        verbose_name=_("Address"),
        max_length=255,
    )
    city = models.CharField(
        verbose_name=_("City"),
        max_length=255,
    )
    state = models.CharField(
        verbose_name=_("State"),
        max_length=2,
    )
    zipcode = models.CharField(
        verbose_name=_("Zip code"),
        max_length=10,
    )
    country = models.CharField(
        verbose_name=_("Country"),
        max_length=255,
    )
    phone = models.CharField(
        verbose_name=_("Phone number"),
        max_length=20,
    )
    first_name = models.CharField(
        verbose_name=_("First name"),
        max_length=255,
    )
    last_name = models.CharField(
        verbose_name=_("Last name"),
        max_length=255,
    )
    email = models.EmailField(
        verbose_name=_("Email"),
        max_length=255,
    )
    work_phone = models.CharField(
        verbose_name=_("Work Phone number"),
        max_length=20,
        blank=True,
    )
    mobile_phone = models.CharField(
        verbose_name=_("Mobile Phone number"),
        max_length=20,
        blank=True,
    )
    fax = models.CharField(
        verbose_name=_("Fax number"),
        max_length=15,
    )
    contact_methods = models.CharField(
        verbose_name=_("Contact methods"),
        max_length=255,
    )

    class Meta:
        verbose_name = _("Member")
        verbose_name_plural = _("Members")

    def __str__(self) -> str:
        return self.name

    # pylint: disable=invalid-name, attribute-defined-outside-init
    def renew(self) -> typing.Self:
        """Renew member in contract for new campaign."""
        self.id = None
        return self
