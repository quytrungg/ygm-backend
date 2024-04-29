from django.db import models

from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.permissions import AllowChamberAdmin, IsCampaignInProgress
from apps.core.api.views import ChamberBaseViewSet

from ....models import Team, UserCampaign
from .. import serializers


class TeamViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    UpdateModelWithoutPatchMixin,
    ChamberBaseViewSet,
):
    """Team management for chamber admin and super admin."""

    queryset = Team.objects.all()
    serializer_class = serializers.TeamDetailSerializer
    ordering_fields = (
        "name",
    )
    serializers_map = {
        "list": serializers.TeamDetailSerializer,
        "create": serializers.TeamWriteSerializer,
        "update": serializers.TeamWriteSerializer,
        "options": serializers.TeamProfileSerializer,
        "info": serializers.TeamReadSerializer,
        "default": serializers.TeamDetailSerializer,
    }
    permissions_map = {
        "list": (AllowChamberAdmin,),
        "retrieve": (AllowChamberAdmin,),
        "options": (AllowChamberAdmin,),
        "info": (AllowChamberAdmin,),
        "default": (AllowChamberAdmin, IsCampaignInProgress),
    }
    search_fields = (
        "name",
        "campaign__name",
    )

    def get_queryset(self):
        """Return list of teams with number of volunteers and team members."""
        campaign = getattr(self.request, "campaign", None)
        qs = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return qs

        if not campaign:
            return qs.none()

        qs = qs.filter(campaign=campaign)
        prefetch_obj = models.Prefetch(
            "members",
            queryset=UserCampaign.objects.all(),
            to_attr="team_members",
        )
        volunteers_count_expr = models.Count(
            "members",
            filter=models.Q(members__deleted_at__isnull=True),
        )
        return qs.prefetch_related(prefetch_obj).annotate(
            volunteers_count=volunteers_count_expr,
        )

    @action(detail=False, methods=("get",))
    def options(self, *args, **kwargs) -> Response:
        """Return list of teams available in campaign."""
        campaign = getattr(self.request, "campaign", None)
        qs = super().get_queryset().filter(campaign=campaign)
        data = qs.values("id", "name")
        serializer = self.get_serializer(data, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=("get",))
    def info(self, *args, **kwargs) -> Response:
        """Return list of teams without members data included."""
        teams = self.get_queryset()
        serializer = self.get_serializer(teams, many=True)
        return Response(serializer.data)
