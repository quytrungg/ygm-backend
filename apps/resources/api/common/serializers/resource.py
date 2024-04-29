from rest_framework import serializers

from s3direct.api.fields import S3DirectUploadURLField

from apps.core.api.serializers import ModelBaseSerializer

from ....models import Resource


class ResourceSerializer(ModelBaseSerializer):
    """Represent serializer for Resource objects."""

    file = S3DirectUploadURLField()
    category_name = serializers.CharField(
        read_only=True,
        source="category.name",
    )
    parent_category_name = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = Resource
        fields = (
            "id",
            "name",
            "file",
            "category",
            "category_name",
            "parent_category_name",
            "user_group",
            "file_type",
        )
