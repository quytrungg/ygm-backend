import typing

from django.conf import settings
from django.contrib.postgres.fields import ArrayField, CIEmailField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from imagekit import models as imagekitmodels
from imagekit.processors import Transpose
from knox.models import AuthToken
from safedelete.managers import (
    SafeDeleteAllManager,
    SafeDeleteDeletedManager,
    SafeDeleteManager,
)

from apps.core.constants import MAX_PHONE_NUMBER_LENGTH, MAX_ZIP_CODE_LENGTH
from apps.core.models import BaseModel

from .. import constants
from ..querysets import UserCampaignQuerySet


class UserCampaign(BaseModel):
    """Stores historical user profile within campaign.

    Stores info about user inside certain campaign. Also,
    provide relation to the team inside the campaign.

    Attributes:
        - first_name: User's first name within campaign
        - last_name: User's last name within campaign
        - email: User's email within campaign
        - role: User's role withing campaign
        - avatar: User's avatar within campaign
        - company_name: name of company user works for campaign
        - company_address: address of company user works for campaign
        - company_city: city of company user works for campaign
        - company_state: state of company user works for campaign
        - company_zip_code: zip code of company user works for campaign
        - company_phone_number: phone number of company user works for campaign
        - company_mobile_number: mobile number of company user works
            for campaign
        - title: title of user within campaign
        - preferred_contact_methods: preferred contact methods
            of the company user works for campaign
        - campaign: Campaign FK
        - team: Team FK
        - user: FK to base user

    """

    first_name = models.CharField(
        verbose_name=_("First name"),
        max_length=30,
    )
    last_name = models.CharField(
        verbose_name=_("Last name"),
        max_length=30,
    )
    email = CIEmailField(
        verbose_name=_("Email address"),
        max_length=254,  # to be compliant with RFCs 3696 and 5321
    )
    mobile_phone = models.CharField(
        verbose_name=_("Mobile phone"),
        max_length=MAX_PHONE_NUMBER_LENGTH,
        blank=True,
    )
    work_phone = models.CharField(
        verbose_name=_("Work phone"),
        max_length=MAX_PHONE_NUMBER_LENGTH,
        blank=True,
    )
    is_active = models.BooleanField(
        verbose_name=_("Is active"),
        default=True,
    )
    role = models.CharField(
        max_length=255,
        choices=constants.UserCampaignRole.choices,
        verbose_name=_("Role"),
        default=constants.UserCampaignRole.VOLUNTEER,
    )
    avatar = imagekitmodels.ProcessedImageField(
        verbose_name=_("Avatar"),
        blank=True,
        null=True,
        upload_to=settings.DEFAULT_MEDIA_PATH,
        max_length=512,
        processors=[Transpose()],
        options={
            "quality": 100,
        },
    )
    company_name = models.CharField(
        max_length=255,
        verbose_name=_("Company name"),
        blank=True,
    )
    company_address = models.CharField(
        max_length=255,
        verbose_name=_("Company address"),
        blank=True,
    )
    company_city = models.CharField(
        max_length=255,
        verbose_name=_("Company city"),
        blank=True,
    )
    company_state = models.CharField(
        max_length=2,
        verbose_name=_("Company state"),
        blank=True,
    )
    company_zip_code = models.CharField(
        max_length=MAX_ZIP_CODE_LENGTH,
        verbose_name=_("Company zip code"),
        blank=True,
    )
    company_phone_number = models.CharField(
        max_length=MAX_PHONE_NUMBER_LENGTH,
        verbose_name=_("Company phone number"),
        blank=True,
    )
    company_mobile_number = models.CharField(
        max_length=MAX_PHONE_NUMBER_LENGTH,
        verbose_name=_("Company fax number"),
        blank=True,
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
        blank=True,
    )
    preferred_contact_methods = ArrayField(
        base_field=models.CharField(max_length=255, blank=True),
        verbose_name=_("Preferred contact methods"),
        default=list,
    )
    campaign = models.ForeignKey(
        to="campaigns.Campaign",
        on_delete=models.CASCADE,
        verbose_name=_("Campaign"),
    )
    sales_goal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
    )
    team = models.ForeignKey(
        to="campaigns.Team",
        on_delete=models.CASCADE,
        verbose_name=_("Team"),
        related_name="members",
        null=True,
    )
    user = models.ForeignKey(
        to="users.User",
        on_delete=models.CASCADE,
        verbose_name=_("Base User"),
        related_name="user_campaigns",
    )
    member = models.ForeignKey(
        to="chambers.StoredMember",
        on_delete=models.SET_NULL,
        verbose_name=_("Stored Member"),
        related_name="user_campaigns",
        null=True,
        blank=True,
    )
    external_user_id = models.IntegerField(
        verbose_name=_("ID in old DB"),
        blank=True,
        null=True,
    )
    external_campaign_id = models.IntegerField(
        verbose_name=_("Campaign ID in old DB"),
        blank=True,
        null=True,
    )
    external_team_id = models.IntegerField(
        verbose_name=_("Team ID in old DB"),
        blank=True,
        null=True,
    )
    deactivated_at = models.DateTimeField(
        verbose_name=_("Deactivated At"),
        blank=True,
        null=True,
    )

    objects = SafeDeleteManager(queryset_class=UserCampaignQuerySet)
    all_objects = SafeDeleteAllManager(queryset_class=UserCampaignQuerySet)
    deleted_objects = SafeDeleteDeletedManager(
        queryset_class=UserCampaignQuerySet,
    )

    class Meta:
        verbose_name = _("User Campaign")
        verbose_name_plural = _("User Campaigns")

    def __str__(self):
        return f"{self.full_name} ({self.email}) ({self.id})"

    @property
    def full_name(self) -> str:
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_invitation_email_sent(self) -> bool:
        """Return if email was sent."""
        return bool(self.email)

    @property
    def is_imported_user(self) -> bool:
        """Return if user campaign is imported from old db."""
        return bool(
            self.external_user_id
            or self.external_campaign_id
            or self.external_team_id,
        )

    @property
    def contact_info(self) -> dict:
        """Return the contact info."""
        return {
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "mobile_phone": self.mobile_phone,
            "work_phone": self.work_phone,
        }

    # pylint: disable=invalid-name, attribute-defined-outside-init
    def renew(self, campaign, team=None) -> typing.Self:
        """Renew a user campaign with new campaign."""
        self.campaign = campaign
        self.team = team
        self.id = None
        return self

    def clean(self):
        """Clean data.

        - Verify that role and team satisfy constraints.

        """
        if (
            self.role == constants.UserCampaignRole.VICE_CHAIR
            and not self.campaign.has_vice_chairs
        ):
            raise ValidationError(
                {"role": _("Campaign does not have vice chairs.")},
            )

        if self.role in (
            constants.UserCampaignRole.CHAMBER_CHAIR,
            constants.UserCampaignRole.VICE_CHAIR,
        ) and self.team:
            error_message = _(
                f"{self.full_name} can't be "
                f"{constants.UserCampaignRole(self.role).label} and be in a "
                "team at the same time.",
            )
            raise ValidationError({"role": error_message})
        if (
            self.role == constants.UserCampaignRole.TEAM_CAPTAIN
            and self.team
            and self.team.captain
            and self.team.captain[0].id != self.id
        ):
            error_message = _(
                f"Team Captain already exists in {self.team.name} team.",
            )
            raise ValidationError({"team": error_message})

    def deactivate(self):
        """Set user campaign deactivation time."""
        self.deactivated_at = timezone.now()
        self.save(update_fields=["deactivated_at"])
        AuthToken.objects.filter(
            user=self.user,
        ).update(expiry=self.deactivated_at)

    def activate(self):
        """Activate user in case it was deactivated."""
        self.deactivated_at = None
        self.save(update_fields=["deactivated_at"])
