from rest_framework import mixins, response
from rest_framework.decorators import action

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.permissions import AllowChamberAdmin, IsCampaignInProgress
from apps.core.api.views import ChamberBaseViewSet

from ....models import Campaign
from ....services import get_inventory_stats
from ...common.serializers import CampaignDetailSerializer
from .. import serializers


class CampaignViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    UpdateModelWithoutPatchMixin,
    ChamberBaseViewSet,
):
    """Viewset for chamber admin to manage Campaigns.

    For campaign in `created` or `open` status, allow to update all fields.
    For campaign in `live` status:
        - if the updated status is `done`, it will only update the status.
        - otherwise, a 400 error will be raised.
    For campaign in `done` status, no update is allowed.

    """

    queryset = Campaign.objects.all()
    serializer_class = CampaignDetailSerializer
    serializers_map = {
        "get_inventory_stats": serializers.CampaignInventoryStatsSerializer,
        "default": CampaignDetailSerializer,
    }
    permissions_map = {
        "update": (
            AllowChamberAdmin,
            IsCampaignInProgress,
        ),
        "default": (AllowChamberAdmin,),
    }
    ordering_fields = ()
    search_fields = ()

    def get_queryset(self):
        """Return only campaigns within the chamber."""
        if getattr(self, "swagger_fake_view", False):
            return self.queryset.none()
        qs = super().get_queryset()
        return qs.filter(
            chamber_id=self.request.user.chamber_id,
        ).order_by("-id")

    @action(detail=False, methods=("get",), url_path="inventory-stats")
    def get_inventory_stats(self, *args, **kwargs):
        """Return overall statistics of inventory."""
        campaign = getattr(self.request, "campaign", None)
        stats = get_inventory_stats(campaign)
        serializer = self.get_serializer(stats)
        return response.Response(serializer.data)
