from apps.core.api.serializers import ModelBaseSerializer

from ....models import TimelineCategory


class TimelineCategorySerializer(ModelBaseSerializer):
    """Provide serializer for TimelineCategory model (get methods only)."""

    class Meta:
        model = TimelineCategory
        fields = (
            "id",
            "name",
        )
