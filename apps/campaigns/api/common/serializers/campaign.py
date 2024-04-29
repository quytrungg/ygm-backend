from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from apps.core.api.permissions import IsCampaignOpen
from apps.core.api.serializers import ModelBaseSerializer, TimezoneChoiceField

from ....constants import UserCampaignRole
from ....models import Campaign, UserCampaign
from ....services import complete_campaign


class CampaignDetailSerializer(ModelBaseSerializer):
    """Base serializer for Campaigns management."""

    pre_trc_income = serializers.DecimalField(
        source="chamber.pre_income",
        coerce_to_string=False,
        max_digits=15,
        decimal_places=2,
        read_only=True,
    )
    status = serializers.ChoiceField(
        choices=Campaign.STATUSES.choices,
        required=False,
    )
    timezone = TimezoneChoiceField()

    class Meta:
        model = Campaign
        fields = (
            "id",
            "name",
            "status",
            "is_renewed",
            "year",
            "start_date",
            "end_date",
            "goal",
            "timeline",
            "pre_trc_income",
            "report_close_weekday",
            "report_close_time",
            "timezone",
            "has_vice_chairs",
            "has_trades",
        )
        extra_kwargs = {
            "is_renewed": {"read_only": True},
            "end_date": {"required": True, "allow_null": False},
            "start_date": {"read_only": True},
            "year": {"required": False},
            "report_close_weekday": {"required": True, "allow_null": False},
            "report_close_time": {"required": True, "allow_null": False},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        open_campaign_statuses = IsCampaignOpen.allowed_statuses
        if (
            self.instance
            and isinstance(self.instance, Campaign)
            and self.instance.status in open_campaign_statuses
            and hasattr(self, "initial_data")
            and self.initial_data.get("status") in open_campaign_statuses
        ):
            self.fields["end_date"].allow_null = True

    def validate(self, attrs: dict) -> dict:
        """Validate data correctness.

        - Campaign which is LIVE can only be set to DONE.
        - Campaign which is DONE can not be updated.

        """
        attrs = super().validate(attrs)
        status = attrs.get("status")

        if not self.instance:
            return attrs
        if (
            status == Campaign.STATUSES.LIVE
            and not UserCampaign.objects.filter(
                campaign=self.instance,
                role=UserCampaignRole.CHAMBER_CHAIR,
            ).exists()
        ):
            raise serializers.ValidationError(
                {
                    "status": _(
                        "Campaign must have chamber chair before going live.",
                    ),
                },
            )
        if (
            status == Campaign.STATUSES.RENEWAL
            and not self.instance.is_renewed
        ):
            raise serializers.ValidationError(
                {"status": _("Campaign cannot be updated to this status.")},
            )
        if self.instance.status == Campaign.STATUSES.LIVE:
            if status != Campaign.STATUSES.DONE:
                raise serializers.ValidationError(
                    {"status": _("Live campaign can only be set to done.")},
                )
            attrs = {"status": status}
        return attrs

    def create(self, validated_data):
        """Disallow creation using this serializer."""
        raise NotImplementedError("Disallowed operation.")

    def update(self, instance, validated_data):
        """Set the `start_date` if status is updated to LIVE."""
        status = validated_data.get("status")
        if status == Campaign.STATUSES.LIVE and not instance.start_date:
            validated_data["start_date"] = timezone.now().date()
        if (
            instance.status != Campaign.STATUSES.DONE
            and status == Campaign.STATUSES.DONE
        ):
            complete_campaign(campaign=instance)
        return super().update(instance, validated_data)
