from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from drf_spectacular.utils import extend_schema_serializer
from s3direct.api.fields import S3DirectUploadURLField

from apps.core.api.serializers import ModelBaseSerializer
from apps.users.constants import UserRole

from ....models import Resource


@extend_schema_serializer(component_name="ResourceCA")
class ResourceSerializer(ModelBaseSerializer):
    """Represent serializer for Chamber Resource objects."""

    file = S3DirectUploadURLField()
    category_name = serializers.CharField(read_only=True)

    def validate_user_group(self, value: list):
        """Validate user group.

        CA shouldn't be able to change user group to SA.

        """
        if UserRole.SUPER_ADMIN in value:
            raise serializers.ValidationError(
                _("Cannot assign super admin role to resources"),
            )
        return value

    def validate(self, attrs: dict) -> dict:
        """Check that category related to chamber."""
        attrs = super().validate(attrs)
        category = attrs.get("category")
        user = self.context.get("request").user
        if user.chamber_id != category.chamber_id:
            raise serializers.ValidationError({
                "category": _("Invalid Category."),
            })
        return attrs

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
