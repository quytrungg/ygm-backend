from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from timezone_field import TimeZoneField

from apps.core.constants import AvailableTimezone
from apps.core.models import BaseModel

from ..constants import CampaignStatus


class Campaign(BaseModel):
    """Represent a campaign in DB.

    Attributes:
        - name: name of campaign
        - status: statuses occured in a campaign
        - year: year when campaign takes place
        - timeline: campaign timeline
        - goal: amount of money collected after a campaign
        - chamber: chamber id that campaign belongs to
        - report_close_weekday: weekday on which weekly reports close
        - report_close_time: time at which weekly reports close
        - timezone: used to calculate stats which need to deal with local time
        - has_vice_chairs: whether campaign has vice chairs
        - has_trades: whether campaign has trades

    """

    name = models.CharField(
        verbose_name=("Name"),
        max_length=255,
        db_collation="case_insensitive",
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=20,
        choices=CampaignStatus.choices,
        default=CampaignStatus.CREATED,
    )
    is_renewed = models.BooleanField(
        verbose_name=_("Is Renewed"),
        default=False,
    )
    year = models.IntegerField(
        verbose_name=_("Year"),
    )
    start_date = models.DateField(
        verbose_name=_("Start Date to be Active"),
        null=True,
        blank=True,
    )
    end_date = models.DateField(
        verbose_name=_("End Date"),
        null=True,
        blank=True,
    )
    timeline = models.ForeignKey(
        to="timelines.TimelineType",
        verbose_name=_("Timeline Applied"),
        on_delete=models.SET_NULL,
        related_name="campaigns",
        null=True,
    )
    goal = models.DecimalField(
        verbose_name=_("Goal"),
        decimal_places=2,
        max_digits=15,
        null=True,
        blank=True,
    )
    chamber = models.ForeignKey(
        to="chambers.Chamber",
        verbose_name=_("Chamber ID"),
        related_name="campaigns",
        on_delete=models.CASCADE,
    )
    report_close_weekday = models.IntegerField(
        verbose_name=_("Report Close Weekday"),
        blank=True,
        null=True,
    )
    report_close_time = models.TimeField(
        verbose_name=_("Report Close Time"),
        blank=True,
        null=True,
    )
    timezone = TimeZoneField(
        verbose_name=_("Timezone"),
        blank=True,
        default=AvailableTimezone.US_CENTRAL,
    )
    has_vice_chairs = models.BooleanField(
        verbose_name=_("Has Vice Chairs"),
        default=False,
    )
    has_trades = models.BooleanField(
        verbose_name=_("Has Trades"),
        default=False,
    )
    external_id = models.IntegerField(
        verbose_name=_("ID in old DB"),
        blank=True,
        null=True,
    )
    external_chamber_id = models.IntegerField(
        verbose_name=_("Chamber ID in old DB"),
        null=True,
        blank=True,
    )
    external_type = models.CharField(
        verbose_name=_("Type In Old DB"),
        max_length=50,
        blank=True,
    )
    external_position = models.IntegerField(
        verbose_name=_("Position in Old DB"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")

    def __str__(self) -> str:
        return self.name

    STATUSES = CampaignStatus

    # pylint: disable=invalid-name, attribute-defined-outside-init
    def renew(self, name, year) -> None:
        """Renew a campaign object."""
        self.id = None
        self.name = name
        self.status = CampaignStatus.CREATED
        self.is_renewed = True
        self.year = year
        self.start_date = None
        self.end_date = None
        self.clean()
        self.save()

    def clean_end_date(self):
        """Make sure end date is after start date and in the future."""
        if not self.end_date or self.status == CampaignStatus.DONE:
            return
        if self.end_date <= timezone.now().date():
            raise ValidationError("End date must be in the future.")
        if not self.start_date:
            return
        if self.end_date < self.start_date:
            raise ValidationError("End date must be after start date.")

    def clean(self):
        """Check if campaign data violates any rules.

        - No campaigns of the same chamber have same name.
        - Only one ongoing campaign per chamber.

        """
        super().clean()
        chamber_campaigns = Campaign.objects.filter(
            chamber_id=self.chamber_id,
        ).exclude(id=self.id)
        errors = {}
        if chamber_campaigns.filter(name=self.name).exists():
            errors["name"] = _("Campaign with this name already exists.")
        if self.status != CampaignStatus.DONE:
            if chamber_campaigns.filter(
                ~models.Q(status=Campaign.STATUSES.DONE),
            ).exists():
                errors["status"] = _("There is an ongoing campaign.")
        if errors:
            raise ValidationError(errors)
