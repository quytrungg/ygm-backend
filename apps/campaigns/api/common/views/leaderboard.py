from django.db import models

from rest_framework import mixins

from ....constants import UserCampaignRole
from ....models import Team, UserCampaign
from .. import serializers


class LeaderBoardViewSetMixin(mixins.ListModelMixin):
    """Provide common logic for leaderboard APIs."""

    queryset = UserCampaign.objects.all()
    ordering_fields = (
        "total_revenue",
        "week_revenue",
        "id",
    )
    search_fields = ()

    def get_queryset(self):
        """Return volunteers of current campaign."""
        qs = super().get_queryset()
        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()
        qs = qs.filter(campaign_id=campaign.id)
        return qs

    def get_revenue_range_filter(self):
        """Return the time range for filtering revenue."""
        if getattr(self, "swagger_fake_view", False):
            return None, None
        revenue_filter_serializer = serializers.RevenueFilterSerializer(
            data=self.request.query_params,
        )
        revenue_filter_serializer.is_valid(raise_exception=True)
        validated_data = revenue_filter_serializer.validated_data
        return validated_data["revenue_from"], validated_data["revenue_to"]


class VolunteerStandingBaseViewSet(LeaderBoardViewSetMixin):
    """Provide logic for Volunteer Standing API."""

    serializer_class = serializers.UserCampaignStandingSerializer

    def get_queryset(self):
        """Annotate information about volunteer's generated revenue."""
        qs = super().get_queryset()
        revenue_from, revenue_to = self.get_revenue_range_filter()
        qs = qs.with_total_revenue().with_week_revenue(
            revenue_from=revenue_from,
            revenue_to=revenue_to,
        ).with_total_cash_revenue().with_total_trade_revenue()
        return qs


# pylint: disable=no-member
class LeadershipStandingBaseViewSet(LeaderBoardViewSetMixin):
    """Provide logic for Leadership Standing API."""

    serializer_class = serializers.UserCampaignLeadershipStandingSerializer

    def get_queryset(self):
        """Annotate information about volunteer's managed teams' revenue."""
        qs = super().get_queryset()
        campaign = getattr(self.request, "campaign", None)
        teams_managing_role = (
            UserCampaignRole.VICE_CHAIR
            if getattr(campaign, "has_vice_chairs", False)
            else UserCampaignRole.CHAMBER_CHAIR
        )
        qs = qs.filter(role=teams_managing_role)
        revenue_from, revenue_to = self.get_revenue_range_filter()
        return (
            qs
            .with_managed_teams_week_revenue(revenue_from, revenue_to)
            .with_managed_teams_total_revenue()
            .with_managed_team_total_cash_revenue()
        )


# pylint: disable=no-member
class TeamStandingBaseViewSet(LeaderBoardViewSetMixin):
    """Provide logic for Team Standing API."""

    serializer_class = serializers.UserCampaignTeamStandingSerializer
    ordering_fields = (
        "total_revenue",
        "id",
    )

    def get_queryset(self):
        """Annotate information about volunteer's managed teams' revenue."""
        qs = super().get_queryset()
        campaign = getattr(self.request, "campaign", None)
        teams_managing_role = (
            UserCampaignRole.VICE_CHAIR
            if getattr(campaign, "has_vice_chairs", False)
            else UserCampaignRole.CHAMBER_CHAIR
        )
        qs = qs.filter(role=teams_managing_role)
        revenue_from, revenue_to = self.get_revenue_range_filter()
        return qs.with_managed_teams_total_revenue().prefetch_related(
            models.Prefetch(
                "managed_teams",
                queryset=Team.objects.all().with_week_revenue(
                    revenue_from=revenue_from,
                    revenue_to=revenue_to,
                ).with_total_cash_revenue().with_total_revenue(),
            ),
        )
