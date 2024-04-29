import decimal

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from apps.core.api.serializers import (
    BaseReorderSerializer,
    ModelBaseSerializer,
)
from apps.members.constants import ContractStatus

from ....models import Level, LevelInstance, Product


class ListLevelSerializer(ModelBaseSerializer):
    """Represent list of Level instances."""

    class Meta:
        model = Level
        fields = (
            "id",
            "product_id",
            "name",
            "amount",
            "cost",
            "order",
        )
        extra_kwargs = {
            "cost": {"coerce_to_string": False},
        }


class LevelSerializer(ModelBaseSerializer):
    """Represent a Level."""

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
    )

    class Meta:
        model = Level
        fields = (
            "id",
            "product",
            "name",
            "cost",
            "amount",
            "benefits",
            "description",
            "conditions",
        )

        extra_kwargs = {
            "cost": {"min_value": decimal.Decimal("0")},
            "benefits": {"required": True, "allow_blank": False},
        }

    def validate_product(self, product: Product) -> Product:
        """Validate `product` belongs to current user's campaign."""
        if not Product.objects.filter(
            id=product.id,
            category__campaign_id=self.context["request"].campaign.id,
        ).exists():
            raise serializers.ValidationError(
                _("Invalid product"),
            )
        return product

    def validate_amount(self, amount: int) -> int:
        """Validate amount, it can't be less than level's sold amount."""
        if not self.instance:
            return amount

        if amount < 0:
            return amount

        sold_amount = LevelInstance.objects.filter(
            level_id=self.instance.id,
            declined_at__isnull=True,
            contract__isnull=False,
            contract__status=ContractStatus.APPROVED,
        ).count()
        if sold_amount > amount:
            err_msg = _(
                f"Amount can't be less than sold amount ({sold_amount}).",
            )
            raise serializers.ValidationError(err_msg)
        return amount

    def update(self, instance: Level, validated_data: dict) -> Level:
        """Update level and sync changes to level instances."""
        updated_instance = super().update(instance, validated_data)
        new_cost = validated_data["cost"]
        LevelInstance.objects.filter(
            level_id=updated_instance.id,
            contract__status=ContractStatus.DRAFT,
        ).update(cost=new_cost)
        return updated_instance


class LevelReorderSerializer(ModelBaseSerializer, BaseReorderSerializer):
    """Represent serializer to reorder levels."""

    class Meta(BaseReorderSerializer.Meta):
        model = Level
