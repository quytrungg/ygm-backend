from rest_framework import mixins

from apps.core.api.views import VolunteerBaseViewSet
from apps.members.constants import ContractStatus

from ....models import LevelInstance
from .. import serializers


class RecentlySoldLevelInstanceViewSet(
    mixins.ListModelMixin,
    VolunteerBaseViewSet,
):
    """Provide viewset for recently sold level instances in VS dashboard."""

    queryset = LevelInstance.objects.filter(
        contract__status=ContractStatus.APPROVED,
        declined_at__isnull=True,
    ).select_related("level", "contract", "contract__member").order_by(
        "-contract__approved_at",
    )
    serializer_class = serializers.RecentlySoldLevelInstanceSerializer
    search_fields = ()
    ordering_fields = ()

    def get_queryset(self):
        """Return level instances within campaign."""
        qs = super().get_queryset()
        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()
        return qs.filter(
            contract__campaign_id=campaign.id,
            contract__created_by__user=self.request.user,
        )
