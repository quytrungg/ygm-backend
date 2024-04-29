from rest_framework import mixins, response
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.permissions import (
    AllowChamberAdmin,
    IsCampaignInProgress,
    IsCampaignOpen,
)
from apps.core.api.views import ChamberBaseViewSet

from .... import services
from ....models import Level
from ...filters import LevelFilter
from .. import serializers


class LevelViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    UpdateModelWithoutPatchMixin,
    mixins.DestroyModelMixin,
    ChamberBaseViewSet,
):
    """Viewset for chamber admin to manage Level."""

    queryset = Level.objects.all().order_by("order")
    serializer_class = serializers.LevelSerializer
    serializers_map = {
        "list": serializers.ListLevelSerializer,
        "reorder": serializers.LevelReorderSerializer,
        "default": serializers.LevelSerializer,
    }
    permissions_map = {
        "list": (AllowChamberAdmin,),
        "retrieve": (AllowChamberAdmin,),
        "update": (
            AllowChamberAdmin,
            IsCampaignInProgress,
        ),
        "reorder": (AllowChamberAdmin, IsCampaignInProgress),
        "default": (AllowChamberAdmin, IsCampaignOpen),
    }
    search_fields = (
        "name",
        "benefits",
        "description",
        "conditions",
    )
    ordering_fields = (
        "name",
    )
    filterset_class = LevelFilter

    def get_queryset(self):
        """Return levels of current user's campaign."""
        qs = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return qs.none()

        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()

        qs = qs.filter(product__category__campaign_id=campaign.id)
        return qs

    @extend_schema(request=None)
    @action(methods=("post",), detail=True)
    def duplicate(self, *args, **kwargs):
        """Duplicate a level."""
        level = self.get_object()
        new_level = services.duplicate_level(level.id)
        return response.Response(data=self.get_serializer(new_level).data)

    @action(detail=True, methods=("put",))
    def reorder(self, request, *args, **kwargs):
        """Reorder items in level list."""
        level = self.get_object()
        serializer = self.get_serializer(level, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)
