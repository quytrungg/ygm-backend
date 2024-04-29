from rest_framework import serializers

from drf_spectacular.utils import extend_schema_serializer

from apps.core.api.serializers import (
    CurrentChamberDefault,
    ModelBaseSerializer,
)

from ....models import ResourceCategory


@extend_schema_serializer(component_name="ResourceCategoryCA")
class ResourceCategorySerializer(ModelBaseSerializer):
    """Represent serializer for Chamber Resource Category objects."""

    chamber_id = serializers.HiddenField(
        default=CurrentChamberDefault(),
    )

    class Meta:
        model = ResourceCategory
        fields = (
            "id",
            "name",
            "chamber_id",
        )
