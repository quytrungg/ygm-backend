from django.db.models import F

from rest_framework import mixins

from apps.core.api.views import VolunteerBaseViewSet

from ....models import Level
from .. import serializers


class RemainingSponsorshipViewSet(
    mixins.ListModelMixin,
    VolunteerBaseViewSet,
):
    """Provide viewset for level remaining sponsorship within campaign."""

    queryset = (
        Level.objects.all()
        .with_remaining_instances_count()
        .with_sold_instances_count()
        .exclude(remaining_instances_count=0)
    )
    serializer_class = serializers.RemainingSponsorshipSerializer
    search_fields = ()
    ordering_fields = (
        "name",
        "product_name",
        "cost",
    )

    def get_queryset(self):
        """Return levels remaining sponsorship of current user's campaign.

        Annotate `product_name` field to the queryset to apply the ordering.

        """
        qs = super().get_queryset().annotate(product_name=F("product__name"))
        campaign = getattr(self.request, "campaign", None)
        if getattr(self, "swagger_fake_view", False) or not campaign:
            return qs.none()
        return qs.filter(product__category__campaign_id=campaign.id)
