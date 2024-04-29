from rest_framework import serializers

from s3direct.api.fields import S3DirectUploadURLField
from safedelete.config import HARD_DELETE

from apps.core.api.serializers import (
    BaseReorderSerializer,
    CurrentTimelineDefault,
    ModelBaseSerializer,
)
from apps.users.api.serializers import UserProfileSerializer

from ....models import Timeline, TimelineAttachment


class TimelineAttachmentSerializer(ModelBaseSerializer):
    """Represent timeline's attachment information."""

    file = S3DirectUploadURLField(required=False, allow_null=True)

    class Meta:
        model = TimelineAttachment
        fields = (
            "id",
            "name",
            "file",
            "content_type",
        )


class TimelineSerializer(ModelBaseSerializer):
    """Provide logic for timeline creation/edit."""

    attachments = TimelineAttachmentSerializer(required=False, many=True)
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    type = serializers.HiddenField(
        default=CurrentTimelineDefault(),
    )

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )
    created_by_data = UserProfileSerializer(
        read_only=True,
        source="created_by",
    )

    class Meta:
        model = Timeline
        fields = (
            "id",
            "name",
            "order",
            "description",
            "due_date",
            "status",
            "category",
            "category_name",
            "created_by",
            "type",
            "assigned_to",
            "created_by_data",
            "attachments",
        )
        extra_kwargs = {
            "assigned_to": {"required": False},
            "order": {"read_only": True},
        }

    def create(self, validated_data):
        """Create timeline with CA's chamber and its attachments."""
        attachments_data = validated_data.pop("attachments", [])
        validated_data["chamber"] = self.context["request"].user.chamber
        created_timeline = super().create(validated_data)
        for attachment in attachments_data:
            attachment["timeline"] = created_timeline

        attachment_serializer = self.fields["attachments"]
        attachment_serializer.create(attachments_data)
        return created_timeline

    def update(self, instance, validated_data):
        """Update timeline and its attachments."""
        attachments_data = validated_data.pop("attachments", [])
        validated_data.pop("timeline", None)
        updated_timeline = super().update(instance, validated_data)
        updated_timeline.attachments.all().delete(force_policy=HARD_DELETE)
        for attachment in attachments_data:
            attachment["timeline"] = updated_timeline

        media_serializer = self.fields["attachments"]
        media_serializer.create(attachments_data)
        return updated_timeline


class TimelineReorderSerializer(ModelBaseSerializer, BaseReorderSerializer):
    """Represent serializer to reorder timelines."""

    class Meta(BaseReorderSerializer.Meta):
        model = Timeline
