from django.db import models

from rest_framework import mixins

from apps.core.api.views import PublicBaseViewSet

from ....models import Level, LevelInstance
from ...filters import LevelFilter, MemberPurchasedLevelFilter
from .. import serializers


class LevelViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    PublicBaseViewSet,
):
    """Provide APIs for volunteers to access Level."""

    queryset = (
        Level.objects.all()
        .with_remaining_instances_count()
        .with_sold_instances_count()
        .order_by("order")
    )
    serializer_class = serializers.LevelDetailSerializer
    serializers_map = {
        "list": serializers.LevelSerializer,
        "default": serializers.LevelDetailSerializer,
    }
    search_fields = ()
    ordering_fields = ()
    filterset_class = LevelFilter

    def get_queryset(self):
        """Return levels of selected campaign."""
        qs = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return qs.none()

        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()
        return qs.filter(product__category__campaign_id=campaign.id)


class MemberPurchasedLevelViewSet(
    mixins.ListModelMixin,
    PublicBaseViewSet,
):
    """Provide APIs to access a member's purchased levels."""

    queryset = Level.objects.all().order_by("order")
    filterset_class = MemberPurchasedLevelFilter
    serializer_class = serializers.MemberPurchasedLevelSerializer
    serializers_map = {
        "list": serializers.MemberPurchasedLevelSerializer,
    }
    search_fields = ()
    ordering_fields = ()

    def get_queryset(self):
        """Return levels of a purchasing member."""
        campaign = getattr(self.request, "campaign", None)
        qs = super().get_queryset()
        if not campaign:
            return qs.none()
        prefetch_instances = models.Prefetch(
            "instances",
            queryset=LevelInstance.objects.filter(
                contract__isnull=False,
                declined_at__isnull=True,
            ).select_related("contract"),
            to_attr="level_instances",
        )
        return qs.filter(
            product__category__campaign_id=campaign.id,
        ).prefetch_related(prefetch_instances)

    def list(self, request, *args, **kwargs):
        """Filter the data returned from serializer."""
        response = super().list(request, *args, **kwargs)
        filtered_data = [
            data for data in response.data["results"] if data["amount"] > 0
        ]
        response.data["results"] = filtered_data
        return response
