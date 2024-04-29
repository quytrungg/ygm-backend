from rest_framework import mixins, response, status
from rest_framework.generics import GenericAPIView

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.permissions import AllowChamberAdmin
from apps.core.api.views import ChamberBaseViewSet

from ....models import Chamber
from .. import serializers


class DashboardAPIView(GenericAPIView):
    """Provide API view for Chamber Admin Dashboard."""

    permission_classes = (AllowChamberAdmin,)
    serializer_class = serializers.DashboardSerializer

    def get(self, *args, **kwargs):
        """Return Chamber Admin Dashboard data."""
        # TODO: Modify this after planning
        return response.Response(
            status=status.HTTP_200_OK,
            data=self.get_dashboard_data(),
        )

    # TODO: Modify this after planning
    def get_dashboard_data(self) -> dict[str, dict[str, int]]:
        """Return the dashboard data for the chamber admin."""
        return {
            "campaign_goal": {
                "current": 20000,
                "total": 100000,
            },
            "volunteers": {
                "current": 12,
                "total": 300,
            },
            "members": {
                "current": 12,
                "total": 300,
            },
            "inventory": {
                "current": 12,
                "total": 300,
            },
        }


class ChamberViewSet(
    UpdateModelWithoutPatchMixin,
    mixins.RetrieveModelMixin,
    ChamberBaseViewSet,
):
    """Viewset for chamber admin to manage Chamber."""

    queryset = Chamber.objects.all()
    serializer_class = serializers.ChamberUpdateSerializer
    serializers_map = {
        "update": serializers.ChamberUpdateSerializer,
    }
    ordering_fields = ()
    search_fields = ()

    def get_object(self):
        """Return the chamber of the chamber admin."""
        return self.request.user.chamber
