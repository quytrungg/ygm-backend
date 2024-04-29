from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field

from apps.core.api.serializers import ModelBaseSerializer
from apps.users.models import User

from ....models import Team, UserCampaign
from .user_campaign import UserCampaignSerializer


class TeamSerializer(ModelBaseSerializer):
    """Serializer for displaying list of team options."""

    members = UserCampaignSerializer(many=True)
    team_captain = serializers.SerializerMethodField()
    volunteers_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = (
            "id",
            "name",
            "goal",
            "team_captain",
            "campaign",
            "volunteers_count",
            "members",
        )

    @extend_schema_field(UserCampaignSerializer())
    def get_team_captain(self, team):
        """Return team captain information."""
        team_captain = UserCampaign.objects.filter(
            team_id=team.id,
            role=User.ROLES.TEAM_CAPTAIN,
        ).first()
        return UserCampaignSerializer(team_captain).data

    def get_volunteers_count(self, team) -> int:
        """Return number of volunteers in team."""
        return UserCampaign.objects.filter(team_id=team.id).count()
