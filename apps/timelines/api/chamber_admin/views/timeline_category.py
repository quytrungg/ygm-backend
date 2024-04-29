from rest_framework import mixins

from apps.core.api.views import ChamberBaseViewSet

from ....models import TimelineCategory
from .. import serializers


class TimelineCategoryViewSet(mixins.ListModelMixin, ChamberBaseViewSet):
    """Provide TimelineCategory CA APIs."""

    queryset = TimelineCategory.objects.all()
    serializer_class = serializers.TimelineCategorySerializer
    ordering_fields = (
        "id",
        "name",
    )
    search_fields = (
        "id",
        "name",
    )
