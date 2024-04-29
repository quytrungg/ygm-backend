from rest_framework import serializers

from apps.core.api.serializers import ModelBaseSerializer

from ....constants import TimelineTypeChoice
from ....models import TimelineType


class TimelineTypeSerializer(ModelBaseSerializer):
    """Provide serializer for TimelineType model (get methods only)."""

    name = serializers.SerializerMethodField()

    class Meta:
        model = TimelineType
        fields = (
            "id",
            "name",
        )

    def get_name(self, timeline_type: TimelineType) -> str:
        """Return timeline type's display label."""
        return TimelineTypeChoice(timeline_type.name).label
