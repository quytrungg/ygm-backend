from rest_framework import serializers

from s3direct.api.fields import S3DirectUploadURLField

from libs.open_api.serializers import OpenApiSerializer

from apps.core.api.serializers import (
    BaseReorderSerializer,
    CurrentCampaignDefault,
    ModelBaseSerializer,
)

from ....models import ProductCategory


class ListProductCategorySerializer(ModelBaseSerializer):
    """Represent list of ProductCategory instances."""

    product_count = serializers.IntegerField()

    class Meta:
        model = ProductCategory
        fields = (
            "id",
            "name",
            "order",
            "product_count",
        )


class ProductCategorySerializer(ModelBaseSerializer):
    """Represent detail information of ProductCategory."""

    image = S3DirectUploadURLField(allow_blank=False, allow_null=True)
    background_color = serializers.CharField(
        allow_blank=True,
        max_length=7,
    )
    campaign = serializers.HiddenField(
        default=CurrentCampaignDefault(),
    )

    class Meta:
        model = ProductCategory
        fields = (
            "id",
            "name",
            "image",
            "background_color",
            "campaign",
        )

    def validate(self, attrs: dict) -> dict:
        """Validate data before saving.

        Ensure that one of 2 fields is provided: image or color.

        """
        if not attrs.get("image") and not attrs.get("background_color"):
            raise serializers.ValidationError(
                "You must provide either image or color field",
            )

        if attrs.get("image") and attrs.get("background_color"):
            raise serializers.ValidationError(
                "You must provide either image or color field, not both",
            )

        return super().validate(attrs)


class ProductCategoryStatsSerializer(OpenApiSerializer):
    """Represent product category's overall statistics."""

    total_value = serializers.DecimalField(
        decimal_places=2,
        max_digits=15,
        coerce_to_string=False,
    )

    class Meta:
        fields = (
            "total_value",
        )


class ProductCategoryUpdateSerializer(ModelBaseSerializer):
    """Represent serializer to update product category's name."""

    class Meta:
        model = ProductCategory
        fields = (
            "id",
            "name",
        )


class ProductCategoryReorderSerializer(
    ModelBaseSerializer,
    BaseReorderSerializer,
):
    """Represent serializer to reorder product categories."""

    class Meta(BaseReorderSerializer.Meta):
        model = ProductCategory
