from django.db.models import Case, Count, F, Value, When
from django.db.models.functions import Coalesce

from rest_framework import mixins, response, status
from rest_framework.decorators import action

from apps.campaigns.tasks import send_volunteers_invitation_emails
from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.permissions import AllowChamberAdmin, IsCampaignInProgress
from apps.core.api.serializers import StringOptionSerializer
from apps.core.api.views import ChamberBaseViewSet
from apps.users.constants import UserRole

from .... import services
from ....constants import ORDERED_ROLES, UserCampaignRole
from ....models import UserCampaign
from ...common.serializers import UserCampaignCompactSerializer
from ...filters import UserCampaignFilter
from ...permissions import IsUserCampaignDeletable
from .. import serializers


class UserCampaignViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    UpdateModelWithoutPatchMixin,
    mixins.DestroyModelMixin,
    ChamberBaseViewSet,
):
    """ViewSet for CA to manage campaign's volunteers."""

    queryset = UserCampaign.objects.all().exclude(
        user__role=UserRole.CHAMBER_ADMIN,
    )
    permissions_map = {
        "roles": (AllowChamberAdmin,),
        "list": (AllowChamberAdmin,),
        "retrieve": (AllowChamberAdmin,),
        "destroy": (
            AllowChamberAdmin,
            IsUserCampaignDeletable,
        ),
        "default": (AllowChamberAdmin, IsCampaignInProgress),
    }
    serializer_class = serializers.UserCampaignCreateSerializer
    serializers_map = {
        "list": UserCampaignCompactSerializer,
        "create": serializers.UserCampaignCreateSerializer,
        "assign_team": serializers.UserCampaignAssignTeamSerializer,
        "roles": StringOptionSerializer,
        "default": serializers.UserCampaignUpdateSerializer,
    }
    search_fields = (
        "first_name",
        "last_name",
    )
    ordering_fields = (
        "first_name",
        "last_name",
        "role_order",
    )
    filterset_class = UserCampaignFilter

    def get_queryset(self):
        """Return volunteers of current campaign."""
        qs = super().get_queryset().annotate(
            role_order=Case(
                *[
                    When(role=role, then=order)
                    for order, role in enumerate(ORDERED_ROLES)
                ],
            ),
        )
        if getattr(self, "swagger_fake_view", False):
            return qs

        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()

        return qs.filter(campaign_id=campaign.id).annotate(
            member_name=Coalesce(F("member__name"), Value("")),
            contract_count=Count("created_contracts"),
        )

    @action(detail=False, methods=["put"], url_path="assign-team")
    def assign_team(self, request, *args, **kwargs) -> response.Response:
        """Assign role to selected user(s) in campaign."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def roles(self, *args, **kwargs) -> response.Response:
        """Return list of user campaign roles."""
        data = [
            {
                "value": role.value,
                "label": role.label,
            }
            for role in UserCampaignRole
            if role != UserCampaignRole.CHAMBER_ADMIN
        ]

        serializer = self.get_serializer(data, many=True)
        return response.Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )

    def perform_destroy(self, instance):
        """Delete user campaign."""
        services.delete_user_campaign(instance)

    @action(detail=True, methods=["post"], url_path="send-registration-link")
    def send_registration_link(self, *args, **kwargs) -> response.Response:
        """Resend registration link for campaign user."""
        user_campaign = self.get_object()
        send_volunteers_invitation_emails.delay([user_campaign.id])
        return response.Response()

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, *args, **kwargs) -> response.Response:
        """Activate user."""
        user_campaign = self.get_object()
        user_campaign.activate()
        return response.Response()

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, *args, **kwargs) -> response.Response:
        """Activate user."""
        user_campaign = self.get_object()
        user_campaign.deactivate()
        return response.Response()
