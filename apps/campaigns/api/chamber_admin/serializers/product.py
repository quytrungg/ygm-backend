
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from safedelete import HARD_DELETE

from apps.core.api.serializers import (
    BaseReorderSerializer,
    ModelBaseSerializer,
)

from ....models import Product, ProductCategory
from ...common.serializers import ProductAttachmentSerializer


class ListProductSerializer(ModelBaseSerializer):
    """Represent list of Product instances to CA."""

    level_count = serializers.IntegerField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "level_count",
            "order",
            "category",
        )


class ProductNameUpdateSerializer(ModelBaseSerializer):
    """Represent serializer to update product's name."""

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
        )


class ProductSerializer(ModelBaseSerializer):
    """Represent detail information of Product."""

    attachments = ProductAttachmentSerializer(
        many=True,
        required=True,
        allow_empty=True,
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
    )

    def validate_category(self, category: ProductCategory) -> ProductCategory:
        """Validate `category` belongs to current user's campaign."""
        if not ProductCategory.objects.filter(
            id=category.id,
            campaign_id=self.context["request"].campaign.id,
        ).exists():
            raise serializers.ValidationError(
                _("Invalid category"),
            )
        return category

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "name",
            "is_included_in_renewal",
            "pre_trc_income",
            "description",
            "attachments",
        )

        extra_kwargs = {
            "pre_trc_income": {"coerce_to_string": False},
        }

    def create(self, validated_data: dict) -> Product:
        """Create product with its attachments."""
        attachments_data = validated_data.pop("attachments", [])
        product = super().create(validated_data)
        for attachment_data in attachments_data:
            attachment_data["product"] = product
        attachment_serializer = self.fields["attachments"]
        attachment_serializer.create(attachments_data)
        return product

    def update(self, instance, validated_data) -> Product:
        """Update product and its attachments."""
        attachments_data = validated_data.pop("attachments", [])
        updated_product = super().update(instance, validated_data)
        updated_product.attachments.all().delete(force_policy=HARD_DELETE)
        for attachment_data in attachments_data:
            attachment_data["product"] = updated_product
        attachment_serializer = self.fields["attachments"]
        attachment_serializer.create(attachments_data)
        return updated_product


class ProductReorderSerializer(ModelBaseSerializer, BaseReorderSerializer):
    """Represent serializer to reorder products."""

    class Meta(BaseReorderSerializer.Meta):
        model = Product
