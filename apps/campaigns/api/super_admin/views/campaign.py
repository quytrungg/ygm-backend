from rest_framework import mixins

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.views import AdminBaseViewSet

from ....models import Campaign
from ...common.serializers import CampaignDetailSerializer
from .. import serializers


class CampaignViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    UpdateModelWithoutPatchMixin,
    AdminBaseViewSet,
):
    """Viewset for super admin to manage Campaigns."""

    queryset = Campaign.objects.all()
    serializer_class = serializers.CampaignSerializer

    ordering_fields = (
        "name",
    )
    search_fields = (
        "name",
        "status",
    )
    serializers_map = {
        "update": CampaignDetailSerializer,
        "default": serializers.CampaignSerializer,
    }
