from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from s3direct.api.fields import S3DirectUploadURLField

from apps.campaigns.models import ProductAttachment
from apps.core.api.serializers import ModelBaseSerializer


class YoutubeEmbedURLValidator:
    """Validate given value is a valid Youtube's embed link."""

    regex = _lazy_re_compile(
        r"^https://www\.youtube\.com/embed/[a-zA-Z0-9_-]{11}(\?.*)?$",
    )

    def __call__(self, data, serializer=None):
        """Return validated embed link."""
        if not self.regex.match(data):
            raise serializers.ValidationError(
                _("Please use a Youtube embed link."),
            )
        return data


class ProductAttachmentSerializer(ModelBaseSerializer):
    """Represent detail information of Product."""

    file = S3DirectUploadURLField(allow_null=True)
    external_url = serializers.URLField(
        allow_blank=True,
        validators=[YoutubeEmbedURLValidator()],
    )

    class Meta:
        model = ProductAttachment
        fields = (
            "id",
            "product_id",
            "name",
            "file",
            "external_url",
            "content_type",
            "order",
        )
        extra_kwargs = {
            "content_type": {"allow_blank": True},
        }

    def validate(self, attrs: dict) -> dict:
        """Return validated data.

        Modify `content_type` based on other fields' values.

        """
        if attrs.get("external_url"):
            attrs["content_type"] = ""
        elif not attrs["content_type"]:
            raise serializers.ValidationError(
                {"content_type": _("This field cannot be blank.")},
            )
        return super().validate(attrs)
