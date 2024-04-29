from django.db import models

from rest_framework import mixins, response
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.permissions import (
    AllowChamberAdmin,
    IsCampaignInProgress,
    IsCampaignOpen,
)
from apps.core.api.views import ChamberBaseViewSet

from .... import services
from ....models import Product
from ...filters import ProductFilter
from .. import serializers


class ProductViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    UpdateModelWithoutPatchMixin,
    mixins.DestroyModelMixin,
    ChamberBaseViewSet,
):
    """Viewset for chamber admin to manage Product."""

    queryset = Product.objects.all().order_by("order")
    serializer_class = serializers.ListProductSerializer
    serializers_map = {
        "list": serializers.ListProductSerializer,
        "update_name": serializers.ProductNameUpdateSerializer,
        "reorder": serializers.ProductReorderSerializer,
        "default": serializers.ProductSerializer,
    }
    permissions_map = {
        "list": (AllowChamberAdmin,),
        "retrieve": (AllowChamberAdmin,),
        "update": (AllowChamberAdmin, IsCampaignInProgress),
        "update_name": (AllowChamberAdmin, IsCampaignInProgress),
        "reorder": (AllowChamberAdmin, IsCampaignInProgress),
        "default": (AllowChamberAdmin, IsCampaignOpen),
    }
    search_fields = (
        "name",
        "description",
    )
    ordering_fields = (
        "name",
    )
    filterset_class = ProductFilter

    def get_queryset(self):
        """Return products of current user's campaign."""
        qs = super().get_queryset()

        if getattr(self, "swagger_fake_view", False):
            return qs.none()

        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()

        qs = qs.filter(category__campaign_id=campaign.id)
        if self.action != "list":
            return qs

        level_count_expr = models.Count(
            "levels",
            filter=models.Q(levels__deleted_at__isnull=True),
        )
        return qs.annotate(
            level_count=level_count_expr,
        )

    @action(detail=True, methods=("put",), url_path="update-name")
    def update_name(self, request, *args, **kwargs):
        """Update product's name."""
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)

    @extend_schema(request=None)
    @action(detail=True, methods=("post",))
    def duplicate(self, *args, **kwargs):
        """Duplicate a product."""
        product = self.get_object()
        new_product = services.duplicate_product(product.id)
        return response.Response(
            data=self.get_serializer(new_product).data,
        )

    @action(detail=True, methods=("put",))
    def reorder(self, request, *args, **kwargs):
        """Reorder items in product list."""
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)
