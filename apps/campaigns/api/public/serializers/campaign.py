from decimal import Decimal

from django.db import models
from django.utils import timezone

from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field

from apps.core.api.serializers import ModelBaseSerializer
from apps.members.models import Contract, Member
from apps.members.services import calculate_total_earnings

from ....constants import UserCampaignRole
from ....models import Campaign, LevelInstance, UserCampaign
from ...common.serializers.user_campaign import UserCampaignSerializer


class CampaignLandingPageSerializer(ModelBaseSerializer):
    """Serializer for getting landing page information of campaign."""

    goal = serializers.DecimalField(
        decimal_places=2,
        max_digits=15,
        coerce_to_string=False,
    )
    campaign_chair = serializers.SerializerMethodField()
    purchasing_members = serializers.SerializerMethodField()
    total_earnings_to_date = serializers.SerializerMethodField()
    total_days = serializers.SerializerMethodField()
    remaining_days = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = (
            "id",
            "name",
            "goal",
            "campaign_chair",
            "purchasing_members",
            "total_earnings_to_date",
            "total_days",
            "remaining_days",
        )

    @extend_schema_field(UserCampaignSerializer)
    def get_campaign_chair(
        self,
        campaign: Campaign,
    ):
        """Return the campaign chair."""
        campaign_chair = UserCampaign.objects.filter(
            campaign=campaign,
            role=UserCampaignRole.CHAMBER_CHAIR,
        ).first()
        if not campaign_chair:
            return None
        return UserCampaignSerializer(campaign_chair).data

    def get_purchasing_members(self, campaign: Campaign) -> int:
        """Return the number of purchasing members."""
        prefetch_instances = models.Prefetch(
            "levels",
            queryset=LevelInstance.objects.all(),
            to_attr="member_instances",
        )
        prefetch_contracts = models.Prefetch(
            "contracts",
            queryset=Contract.objects.all().prefetch_related(
                prefetch_instances,
            ),
            to_attr="member_contracts",
        )
        return Member.objects.filter(
            contracts__campaign_id=campaign.id,
            contracts__status=Contract.STATUSES.APPROVED,
            contracts__approved_at__isnull=False,
        ).prefetch_related(prefetch_contracts).values_list(
            "name",
        ).distinct().count()

    def get_total_earnings_to_date(self, campaign: Campaign) -> Decimal:
        """Return total earnings."""
        return calculate_total_earnings(campaign)

    def get_total_days(self, campaign: Campaign) -> int | None:
        """Return total campaign days."""
        if not campaign.start_date:
            return None
        return (campaign.end_date - campaign.start_date).days

    def get_remaining_days(self, campaign: Campaign) -> int | None:
        """Return remaining campaign days."""
        if not campaign.start_date:
            return None
        return (campaign.end_date - timezone.now().date()).days
