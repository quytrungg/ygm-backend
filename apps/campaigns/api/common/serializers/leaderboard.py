from rest_framework import serializers

from s3direct.api.fields import S3DirectUploadURLField

from libs.open_api.serializers import OpenApiSerializer

from apps.campaigns.models import Team, UserCampaign
from apps.core.api.serializers import ModelBaseSerializer


class RevenueFilterSerializer(OpenApiSerializer):
    """Provide validation for some leaderboard APIs' query params."""

    revenue_from = serializers.DateTimeField()
    revenue_to = serializers.DateTimeField()

    class Meta:
        fields = (
            "revenue_from",
            "revenue_to",
        )


class UserCampaignStandingSerializer(ModelBaseSerializer):
    """Represent UserCampaign information in Volunteer Standings page."""

    avatar = S3DirectUploadURLField()
    total_revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    week_revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    total_cash_revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    total_trade_revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = UserCampaign
        fields = (
            "id",
            "first_name",
            "last_name",
            "role",
            "total_revenue",
            "week_revenue",
            "total_cash_revenue",
            "total_trade_revenue",
            "avatar",
            "company_name",
        )
        extra_kwargs = {
            "company_name": {"default": ""},
        }


class TeamStandingSerializer(ModelBaseSerializer):
    """Represent Team information in Team Standings page."""

    total_revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    week_revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    total_cash_revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = Team
        fields = (
            "id",
            "name",
            "goal",
            "week_revenue",
            "total_revenue",
            "total_cash_revenue",
        )
        extra_kwargs = {
            "goal": {"coerce_to_string": False},
        }


class UserCampaignTeamStandingSerializer(ModelBaseSerializer):
    """Represent UserCampaign information in Team Standings page."""

    managed_teams = TeamStandingSerializer(many=True)

    class Meta:
        model = UserCampaign
        fields = (
            "id",
            "first_name",
            "last_name",
            "role",
            "managed_teams",
        )


class UserCampaignLeadershipStandingSerializer(ModelBaseSerializer):
    """Represent UserCampaign information in Leadership Standings page."""

    total_revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    week_revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    total_cash_revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = UserCampaign
        fields = (
            "id",
            "first_name",
            "last_name",
            "role",
            "total_revenue",
            "week_revenue",
            "total_cash_revenue",
        )
