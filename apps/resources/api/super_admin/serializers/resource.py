from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from drf_spectacular.utils import extend_schema_serializer
from s3direct.api.fields import S3DirectUploadURLField

from apps.core.api.serializers import ModelBaseSerializer

from ....models import Resource


@extend_schema_serializer(component_name="ResourceSA")
class ResourceSerializer(ModelBaseSerializer):
    """Represent serializer for Resource objects."""

    file = S3DirectUploadURLField()
    category_name = serializers.CharField(
        read_only=True,
        source="category.name",
    )

    class Meta:
        model = Resource
        fields = (
            "id",
            "name",
            "file",
            "category",
            "category_name",
            "user_group",
            "file_type",
        )

    def validate(self, attrs: dict) -> dict:
        """Check that category is not related to chamber."""
        attrs = super().validate(attrs)
        category = attrs.get("category")
        if category.chamber_id is not None:
            raise serializers.ValidationError({
                "category": _("Could not use chamber related category."),
            })
        return attrs
