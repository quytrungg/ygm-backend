from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from rest_framework import mixins

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.permissions import AllowAllRoles, AllowChamberUser
from apps.core.api.views import VolunteerBaseViewSet
from apps.users.constants import UserRole

from ....models import Team, UserCampaign
from ...common.serializers import UserCampaignCompactSerializer
from ...filters import UserCampaignFilter
from .. import serializers


class UserCampaignViewSet(
    mixins.ListModelMixin,
    VolunteerBaseViewSet,
):
    """ViewSet for volunteers to access campaign's volunteers."""

    queryset = UserCampaign.objects.all().exclude(
        user__role=UserRole.CHAMBER_ADMIN,
        deactivated_at__isnull=True,
    )
    serializer_class = UserCampaignCompactSerializer
    search_fields = (
        "first_name",
        "last_name",
    )
    ordering_fields = ()
    filterset_class = UserCampaignFilter

    def get_queryset(self):
        """Return volunteers of current campaign."""
        qs = super().get_queryset()
        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()
        return qs.filter(campaign_id=campaign.id)


class ProfileViewSet(
    mixins.RetrieveModelMixin,
    UpdateModelWithoutPatchMixin,
    VolunteerBaseViewSet,
):
    """Viewset for viewing and editing volunteer's profile."""

    queryset = UserCampaign.objects.all().select_related(
        "user",
    ).prefetch_related(
        Prefetch(
            "team",
            queryset=Team.objects.all().with_team_captain(),
        ),
    )
    serializer_class = serializers.ProfileSerializer
    permissions_map = {
        "default": (AllowAllRoles,),
        "update": (AllowChamberUser,),
    }
    search_fields = ()
    ordering_fields = ()

    def get_object(self):
        """Return the current user."""
        user = self.request.user
        if self.is_user_super_admin:
            return user
        campaign = getattr(self.request, "campaign", None)
        return get_object_or_404(
            self.get_queryset(),
            campaign=campaign,
            user=user,
        )

    def get_serializer_class(self):
        """Return custom serializer for SA."""
        if self.is_user_super_admin:
            return serializers.SuperAdminProfileSerializer
        return super().get_serializer_class()
