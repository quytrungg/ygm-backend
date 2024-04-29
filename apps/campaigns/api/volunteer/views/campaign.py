from rest_framework import response
from rest_framework.decorators import action

from apps.core.api.views import VolunteerBaseViewSet

from ....models import Campaign
from ....services import get_vs_dashboard_data
from .. import serializers


class CampaignViewSet(VolunteerBaseViewSet):
    """Viewset for campaign management in VS."""

    queryset = Campaign.objects.all()
    serializer_class = serializers.DashboardStatsSerializer

    @action(methods=("get",), detail=False, url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        """Return campaign's dashboard for VS."""
        campaign = getattr(self.request, "campaign", None)
        if getattr(self, "swagger_fake_view", False) or not campaign:
            return self.queryset.none()
        dashboard_data = get_vs_dashboard_data(campaign, request.user)
        serializer = self.get_serializer(dashboard_data)
        return response.Response(serializer.data)
