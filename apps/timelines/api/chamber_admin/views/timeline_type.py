from rest_framework import mixins

from apps.core.api.views import ChamberBaseViewSet

from ....models import TimelineType
from .. import serializers


class TimelineTypeViewSet(mixins.ListModelMixin, ChamberBaseViewSet):
    """Provide TimelineType viewset for CA."""

    queryset = TimelineType.objects.all()
    serializer_class = serializers.TimelineTypeSerializer
    ordering_fields = ()
    search_fields = ()
