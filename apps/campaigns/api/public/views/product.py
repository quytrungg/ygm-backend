from django.db import models

from rest_framework import mixins

from apps.core.api.views import PublicBaseViewSet
from apps.members.constants import ContractStatus

from ....models import Level, LevelInstance, Product
from ...filters import ProductFilter
from .. import serializers


class ProductViewSet(
    mixins.ListModelMixin,
    PublicBaseViewSet,
):
    """Provide public APIs to access Product."""

    queryset = Product.objects.all().order_by("order")
    serializer_class = serializers.ListProductSerializer
    search_fields = ()
    ordering_fields = ()
    filterset_class = ProductFilter

    def get_queryset(self):
        """Return products of current user's campaign."""
        qs = super().get_queryset()

        if getattr(self, "swagger_fake_view", False):
            return qs.none()

        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()

        prefetch_level_qs = (
            Level.objects.all()
            .order_by("order")
            .with_remaining_instances_count()
            .with_sold_instances_count()
            .prefetch_related(
                models.Prefetch(
                    "instances",
                    to_attr="prefetch_instances",
                    queryset=LevelInstance.objects.all()
                    .filter(
                        declined_at__isnull=True,
                        contract__status=ContractStatus.APPROVED,
                    )
                    .select_related("contract__member"),
                ),
            )
        )
        return qs.filter(
            category__campaign_id=campaign.id,
        ).prefetch_related(
            models.Prefetch(
                "levels",
                to_attr="prefetch_levels",
                queryset=prefetch_level_qs,
            ),
        )
