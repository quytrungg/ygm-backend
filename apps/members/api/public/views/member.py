from django.db import models

from rest_framework import mixins, response
from rest_framework.decorators import action

from apps.campaigns.models import LevelInstance
from apps.core.api.views import PublicBaseViewSet
from apps.members import models as mbr_models
from apps.members.services import calculate_total_earnings

from ...filters import PurchasingMemberFilter
from .. import serializers


class PurchasingMemberViewSet(
    mixins.ListModelMixin,
    PublicBaseViewSet,
):
    """Viewset to manage purchasing members."""

    queryset = mbr_models.Member.objects.filter(
        contracts__isnull=False,
        contracts__deleted_at__isnull=True,
        contracts__status=mbr_models.Contract.STATUSES.APPROVED,
        contracts__approved_at__isnull=False,
    ).order_by("name")
    filterset_class = PurchasingMemberFilter
    serializer_class = serializers.PurchasingMemberSerializer
    serializers_map = {
        "get_total_earnings": serializers.MemberTotalEarningSerializer,
        "default": serializers.PurchasingMemberSerializer,
    }
    search_fields = (
        "name",
    )
    ordering_fields = (
        "name",
        "contracts__approved_at",
    )

    def get_queryset(self):
        """Return information for purchasing members."""
        campaign = getattr(self.request, "campaign", None)
        qs = super().get_queryset()
        if not campaign:
            return qs.none()
        prefetch_instances = models.Prefetch(
            "levels",
            queryset=LevelInstance.objects.all(),
            to_attr="member_instances",
        )
        prefetch_contracts = models.Prefetch(
            "contracts",
            queryset=mbr_models.Contract.objects.filter(
                campaign_id=campaign.id,
                status=mbr_models.Contract.STATUSES.APPROVED,
                approved_at__isnull=False,
            ).prefetch_related(prefetch_instances),
            to_attr="member_contracts",
        )
        return qs.filter(
            contracts__campaign_id=campaign.id,
        ).prefetch_related(prefetch_contracts)

    @action(methods=("get",), detail=False, url_path="total-earnings")
    def get_total_earnings(self, *args, **kwargs) -> response.Response:
        """Return total earnings of all purchasing members."""
        campaign = getattr(self.request, "campaign", None)
        total_earnings = calculate_total_earnings(campaign)
        serializer = self.get_serializer(
            data={"total_earnings": total_earnings},
        )
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data)
