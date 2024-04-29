from rest_framework import mixins, response
from rest_framework.decorators import action

from apps.campaigns import models as campaigns_models
from apps.core.api.views import ChamberBaseViewSet
from apps.reports import services

from .. import serializers


class SaleReportViewSet(mixins.ListModelMixin, ChamberBaseViewSet):
    """Provide endpoints for retrieving sale report data."""

    queryset = campaigns_models.ProductCategory.objects.all()
    serializer_class = serializers.ProductCategorySaleReportSerializer
    serializers_map = {
        "list": serializers.ProductCategorySaleReportSerializer,
        "get_statistics": serializers.SaleStatisticsReportSerializer,
    }
    ordering_fields = ()
    search_fields = ()

    def get_queryset(self):
        """Return product categories with sale report of current campaign."""
        qs = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return qs.none()

        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()

        return qs.filter(campaign_id=campaign.id).with_sale_report_data()

    @action(
        methods=("get",),
        detail=False,
        url_path="statistics",
        url_name="statistics",
    )
    def get_statistics(self, *args, **kwargs):
        """Return sale statistics for current campaign."""
        campaign = getattr(self.request, "campaign", None)
        if getattr(self, "swagger_fake_view", False) or not campaign:
            return response.Response(data={})

        return response.Response(
            data=services.get_sale_statistics_data(campaign.id),
        )
