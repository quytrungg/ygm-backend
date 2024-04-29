from rest_framework import mixins

from apps.core.api.views import PublicBaseViewSet

from ....models import ProductCategory
from .. import serializers


class ProductCategoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    PublicBaseViewSet,
):
    """Provide public APIs to access ProductCategory."""

    queryset = ProductCategory.objects.all().order_by("order")
    serializer_class = serializers.ProductCategorySerializer
    search_fields = (
        "name",
    )
    ordering_fields = ()

    def get_queryset(self):
        """Return product categories of selected chamber's campaign."""
        qs = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return qs.none()
        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()
        return qs.filter(campaign_id=campaign.id)
