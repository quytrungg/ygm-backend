from django.db.models import Prefetch

from rest_framework import mixins

from apps.core.api.views import ChamberBaseViewSet
from apps.members.constants import ContractStatus

from ....models import Level, LevelInstance, Product, ProductCategory
from .. import serializers


class MarketingOpportunitiesViewSet(
    mixins.ListModelMixin,
    ChamberBaseViewSet,
):
    """List campaign's inventory data for marketing opportunities page."""

    queryset = ProductCategory.objects.all().prefetch_related(
        Prefetch(
            "products",
            queryset=Product.objects.all().prefetch_related(
                Prefetch(
                    "levels",
                    queryset=(
                        Level.objects.all()
                        .with_total_instances_count()
                        .with_sold_instances_count()
                        .prefetch_related(
                            Prefetch(
                                "instances",
                                queryset=LevelInstance.objects.filter(
                                    contract__isnull=False,
                                    contract__status__in=(
                                        ContractStatus.APPROVED,
                                        ContractStatus.SIGNED,
                                    ),
                                    declined_at__isnull=True,
                                ).select_related("contract__member"),
                            ),
                        )
                    ),
                ),
            ),
        ),
    ).order_by("order")
    serializer_class = serializers.ProductCategoryMarketingSerializer
    ordering_fields = ()
    search_fields = ()

    def get_queryset(self):
        """Get marketing opportunities data."""
        qs = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return qs.none()
        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()

        return qs.filter(campaign_id=campaign.pk)
