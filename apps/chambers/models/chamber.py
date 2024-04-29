import decimal
import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from safedelete.config import SOFT_DELETE

from apps.campaigns.constants import CampaignStatus
from apps.chambers import constants
from apps.core.models import BaseModel


class Chamber(BaseModel):
    """Represent a chamber.

    Attributes:
        - name: Chamber's name
        - nickname: Chamber's nickname
        - subdomain: Chamber's custom subdomain, each chamber is assigned a
        unique value. Other users will use this subdomain to access chamber's
        campaigns.
        - address: Chamber's physical address
        - city: Chamber's city
        - state: Chamber's state
        - zipcode: Chamber's zipcode
        - country: Chamber's country
        - mail_address: Chamber's mail address
        - mail_city: Chamber's mail city
        - mail_state: Chamber's mail state
        - mail_zipcode: Chamber's mail zipcode
        - mail_country: Chamber's mail country
        - phone: Chamber's phone number
        - member_count: number of members in Chamber
        - city_population: Chamber's city population
        - country_population: Chamber's country population
        - msa_population: Chamber's msa population
        - total_budget: Chamber's total budget
        - total_membership_budget: Chamber's total membership budget
        - pre_income: Chamber's pre-TRC sponsorship income
        - note: Note about Chamber, written by super admin
        - trc_coord_first_name: TRC Coordinator's first name
        - trc_coord_last_name: TRC Coordinator's last name
        - trc_coord_email: TRC Coordinator's email
        - trc_coord_phone: TRC Coordinator's phone
        - trc_coord_title TRC Coordinator's title
        - trc_coord_office_phone: TRC Coordinator's office phone
        - trc_coord_office_phone_ext: TRC Coordinator's phone extension
        - ceo_first_name: CEO's first name
        - ceo_last_name: CEO's last name
        - ceo_email: CEO's email
        - ceo_phone: CEO's phone
        - instagram_url, facebook_url, twitter_url, youtube_url, linkedin_url:
        social links

    """

    _safedelete_policy = SOFT_DELETE

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    nickname = models.CharField(
        verbose_name=_("Nick Name"),
        max_length=255,
        db_collation="case_insensitive",
    )
    subdomain = models.CharField(
        verbose_name=_("Subdomain"),
        max_length=constants.CHAMBER_SUBDOMAIN_MAX_LENGTH,
    )
    address = models.CharField(
        verbose_name=_("Address"),
        max_length=255,
        blank=True,
    )
    city = models.CharField(
        verbose_name=_("City"),
        max_length=50,
        blank=True,
    )
    state = models.CharField(
        verbose_name=_("State"),
        max_length=2,
        blank=True,
    )
    zipcode = models.CharField(
        verbose_name=_("Zipcode"),
        max_length=5,
        blank=True,
    )
    country = models.CharField(
        verbose_name=_("Country"),
        max_length=255,
        blank=True,
    )
    mail_address = models.CharField(
        verbose_name=_("Mail Address"),
        max_length=255,
        blank=True,
    )
    mail_city = models.CharField(
        verbose_name=_("Mail City"),
        max_length=50,
        blank=True,
    )
    mail_state = models.CharField(
        verbose_name=_("Mail State"),
        max_length=2,
        blank=True,
    )
    mail_zipcode = models.CharField(
        verbose_name=_("Mail Zipcode"),
        max_length=5,
        blank=True,
    )
    mail_country = models.CharField(
        verbose_name=_("Mail Country"),
        max_length=255,
        blank=True,
    )
    phone = models.CharField(
        verbose_name=_("Phone"),
        max_length=15,
        blank=True,
    )
    member_count = models.IntegerField(
        verbose_name=_("Number of members"),
        default=0,
    )
    city_population = models.IntegerField(
        verbose_name=_("City's population"),
        default=0,
    )
    country_population = models.IntegerField(
        verbose_name=_("Country's population"),
        default=0,
    )
    msa_population = models.IntegerField(
        verbose_name=_("MSA's population"),
        default=0,
    )
    total_budget = models.DecimalField(
        verbose_name=_("Total budget"),
        decimal_places=3,
        max_digits=13,
        default=decimal.Decimal("0"),
    )
    total_membership_budget = models.DecimalField(
        verbose_name=_("Total membership budget"),
        decimal_places=3,
        max_digits=13,
        default=decimal.Decimal("0"),
    )
    pre_income = models.DecimalField(
        verbose_name=_("Pre-TRC sponsorship income"),
        decimal_places=3,
        max_digits=13,
        default=decimal.Decimal("0"),
    )
    note = models.TextField(
        verbose_name=_("Note"),
        blank=True,
    )
    trc_coord_first_name = models.CharField(
        verbose_name=_("TRC Coord First name"),
        max_length=255,
        blank=True,
    )
    trc_coord_last_name = models.CharField(
        verbose_name=_("TRC Coord Last name"),
        max_length=255,
        blank=True,
    )
    trc_coord_email = models.EmailField(
        verbose_name=_("TRC Coord Email"),
    )
    trc_coord_phone = models.CharField(
        verbose_name=_("TRC Coord Phone"),
        max_length=15,
        blank=True,
    )
    trc_coord_title = models.CharField(
        verbose_name=_("TRC Coord Title"),
        max_length=255,
        blank=True,
    )
    trc_coord_office_phone = models.CharField(
        verbose_name=_("TRC Coord Office Phone"),
        max_length=15,
        blank=True,
    )
    trc_coord_office_phone_ext = models.CharField(
        verbose_name=_("TRC Coord Office Phone ext"),
        max_length=10,
        blank=True,
    )
    ceo_first_name = models.CharField(
        verbose_name=_("CEO First Name"),
        max_length=255,
        blank=True,
    )
    ceo_last_name = models.CharField(
        verbose_name=_("CEO Last Name"),
        max_length=255,
        blank=True,
    )
    ceo_email = models.EmailField(
        verbose_name=_("CEO Email"),
        blank=True,
    )
    ceo_phone = models.CharField(
        verbose_name=_("CEO Phone"),
        max_length=15,
        blank=True,
    )
    instagram_url = models.URLField(
        verbose_name=_("Instagram URL"),
        max_length=255,
        blank=True,
    )
    facebook_url = models.URLField(
        verbose_name=_("Facebook URL"),
        max_length=255,
        blank=True,
    )
    twitter_url = models.URLField(
        verbose_name=_("Twitter URL"),
        max_length=255,
        blank=True,
    )
    youtube_url = models.URLField(
        verbose_name=_("Youtube URL"),
        max_length=255,
        blank=True,
    )
    linkedin_url = models.URLField(
        verbose_name=_("LinkedIn URL"),
        max_length=255,
        blank=True,
    )
    external_id = models.IntegerField(
        verbose_name=_("ID from old db"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Chamber")
        verbose_name_plural = _("Chambers")
        constraints = [
            models.UniqueConstraint(
                fields=("nickname",),
                name="chambers_unique_nickname",
                condition=models.Q(deleted_at__isnull=True),
            ),
            models.UniqueConstraint(
                fields=("subdomain",),
                name="chambers_unique_subdomain",
                condition=models.Q(deleted_at__isnull=True),
            ),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def can_renew_campaign(self) -> bool:
        """Check if chamber is allowed to renew campaign."""
        return (
            self.campaigns.exists()
            and not self.campaigns.exclude(status=CampaignStatus.DONE).exists()
        )

    def clean_subdomain(self):
        """Validate chamber subdomain with business validation."""
        if not self.subdomain:
            return
        subdomain = self.subdomain
        if subdomain.startswith("-") or subdomain.endswith("-"):
            raise ValidationError(
                _("Subdomain cannot start or end with hyphen."),
            )
        if not bool(re.match(constants.VALID_SUBDOMAIN_PATTERN, subdomain)):
            raise ValidationError(
                _("Subdomain must begin and end with an alpha-numeric."),
            )
        if Chamber.objects.filter(
            subdomain=self.subdomain,
        ).exclude(id=self.id).exists():
            raise ValidationError(_("Subdomain already exists."))
        if not self.id:
            return
        instance = Chamber.objects.get(id=self.id)
        if (
            instance.subdomain != self.subdomain
            and self.campaigns.filter(status=CampaignStatus.LIVE).exists()
        ):
            raise ValidationError(
                _("A live campaign already exists. Cannot update subdomain."),
            )
