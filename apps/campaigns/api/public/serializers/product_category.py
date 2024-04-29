from drf_spectacular.utils import extend_schema_serializer
from s3direct.api.fields import S3DirectUploadURLField

from apps.core.api.serializers import ModelBaseSerializer

from ....models import ProductCategory


@extend_schema_serializer(component_name="ProductCategoryPublic")
class ProductCategorySerializer(ModelBaseSerializer):
    """Represent ProductCategory information."""

    image = S3DirectUploadURLField()

    class Meta:
        model = ProductCategory
        fields = (
            "id",
            "name",
            "image",
            "background_color",
        )
