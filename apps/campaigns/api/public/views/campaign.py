from rest_framework import response
from rest_framework.decorators import action

from apps.core.api.views import PublicBaseViewSet

from ....models import Campaign
from .. import serializers


class CampaignViewSet(PublicBaseViewSet):
    """Viewset for public information about Campaigns."""

    queryset = Campaign.objects.all()
    serializer_class = serializers.CampaignLandingPageSerializer

    def get_object(self):
        """Return the campaign of query params's chamber."""
        if getattr(self, "swagger_fake_view", False):
            return self.queryset.none()
        return getattr(self.request, "campaign", None)

    @action(
        detail=False,
        methods=("get",),
        url_path="landing-page",
    )
    def get_landing_page_information(self, *args, **kwargs):
        """Return information for landing page.

        Return 404 if the campaign is not found.

        """
        campaign = self.get_object()
        if not campaign:
            return response.Response(status=404)

        serializer = self.get_serializer(campaign)
        return response.Response(serializer.data)
