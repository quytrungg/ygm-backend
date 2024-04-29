from drf_spectacular.utils import extend_schema_serializer

from apps.core.api.serializers import ModelBaseSerializer

from ....models import ResourceCategory


@extend_schema_serializer(component_name="ResourceCategorySA")
class ResourceCategorySerializer(ModelBaseSerializer):
    """Represent serializer for Resource Category objects."""

    class Meta:
        model = ResourceCategory
        fields = (
            "id",
            "name",
            "chamber",
        )
