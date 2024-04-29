from rest_framework import serializers

from apps.core.api.serializers import (
    CurrentCampaignDefault,
    ModelBaseSerializer,
)
from apps.users.constants import UserRole

from ....models import Team
from ...common.serializers.user_campaign import UserCampaignSerializer


class TeamProfileSerializer(ModelBaseSerializer):
    """Serializer for displaying list of team options."""

    class Meta:
        model = Team
        fields = (
            "id",
            "name",
        )


class TeamReadSerializer(ModelBaseSerializer):
    """Base serializer for read methods of Team model."""

    team_captain = serializers.SerializerMethodField()
    volunteers_count = serializers.IntegerField()

    class Meta:
        model = Team
        fields = (
            "id",
            "name",
            "goal",
            "team_captain",
            "campaign",
            "volunteers_count",
        )

    def get_team_captain(self, team) -> UserCampaignSerializer:
        """Return team captain information."""
        team_captain = None
        for member in team.team_members:
            if member.role != UserRole.TEAM_CAPTAIN:
                continue
            team_captain = member
        return UserCampaignSerializer(team_captain).data


class TeamDetailSerializer(TeamReadSerializer):
    """Detail serializer with members included for Team model."""

    members = UserCampaignSerializer(many=True, source="team_members")

    class Meta(TeamReadSerializer.Meta):
        model = Team
        fields = TeamReadSerializer.Meta.fields + (
            "members",
        )


class TeamWriteSerializer(ModelBaseSerializer):
    """Serializer for write methods with a team in campaign."""

    campaign = serializers.HiddenField(
        default=CurrentCampaignDefault(),
    )

    class Meta:
        model = Team
        fields = (
            "name",
            "goal",
            "campaign",
        )
