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
from ....models import ProductCategory
from .. import serializers


class ProductCategoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    UpdateModelWithoutPatchMixin,
    mixins.DestroyModelMixin,
    ChamberBaseViewSet,
):
    """Viewset for chamber admin to manage ProductCategory."""

    queryset = ProductCategory.objects.all().order_by("order")
    serializer_class = serializers.ProductCategorySerializer
    serializers_map = {
        "list": serializers.ListProductCategorySerializer,
        "get_stats": serializers.ProductCategoryStatsSerializer,
        "update_name": serializers.ProductCategoryUpdateSerializer,
        "reorder": serializers.ProductCategoryReorderSerializer,
        "default": serializers.ProductCategorySerializer,
    }
    permissions_map = {
        "list": (AllowChamberAdmin,),
        "retrieve": (AllowChamberAdmin,),
        "get_stats": (AllowChamberAdmin,),
        "update": (AllowChamberAdmin, IsCampaignInProgress),
        "update_name": (AllowChamberAdmin, IsCampaignInProgress),
        "reorder": (AllowChamberAdmin, IsCampaignInProgress),
        "default": (AllowChamberAdmin, IsCampaignOpen),
    }
    search_fields = (
        "name",
    )
    ordering_fields = (
        "name",
    )

    def get_queryset(self):
        """Return product categories of current user's campaign."""
        qs = super().get_queryset()

        if getattr(self, "swagger_fake_view", False):
            return qs.none()

        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()

        qs = qs.filter(campaign_id=campaign.id)
        if self.action != "list":
            return qs

        product_count_expr = models.Count(
            "products",
            filter=models.Q(products__deleted_at__isnull=True),
        )
        return qs.annotate(
            product_count=product_count_expr,
        )

    @action(detail=True, methods=("get",), url_path="stats")
    def get_stats(self, *args, **kwargs):
        """Return overall statistics of selected product category."""
        category = self.get_object()
        stats = services.get_product_category_stats(category)
        serializer = self.get_serializer(stats)
        return response.Response(data=serializer.data)

    @action(detail=True, methods=("put",), url_path="update-name")
    def update_name(self, request, *args, **kwargs) -> response.Response:
        """Update product category's name."""
        product_category = self.get_object()
        serializer = self.get_serializer(product_category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)

    @action(detail=True, methods=("put",))
    def reorder(self, request, *args, **kwargs) -> response.Response:
        """Reorder items in product category/inventory list."""
        category = self.get_object()
        serializer = self.get_serializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response()

    @extend_schema(request=None)
    @action(detail=True, methods=("post",))
    def duplicate(self, *args, **kwargs):
        """Duplicate a category and products/levels beneath it."""
        product_category = self.get_object()
        new_category = services.duplicate_category(product_category.id)
        return response.Response(
            data=self.get_serializer(new_category).data,
        )
