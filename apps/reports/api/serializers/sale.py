from decimal import Decimal

from rest_framework import serializers

from apps.campaigns import models as campaigns_models
from apps.core.api.serializers import BaseSerializer, ModelBaseSerializer


class LevelSaleReportSerializer(ModelBaseSerializer):
    """Represent Level's sale report info."""

    sold_instances_count = serializers.IntegerField()
    total_instances_count = serializers.IntegerField()
    sold_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    remaining_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = campaigns_models.Level
        fields = (
            "id",
            "name",
            "cost",
            "sold_instances_count",
            "total_instances_count",
            "sold_value",
            "remaining_value",
        )
        extra_kwargs = {
            "cost": {"coerce_to_string": False},
        }


class ProductSaleReportSerializer(ModelBaseSerializer):
    """Represent Product's sale report info."""

    levels = LevelSaleReportSerializer(many=True, source="prefetched_levels")
    sold_value = serializers.SerializerMethodField()
    remaining_value = serializers.SerializerMethodField()
    unlimited_levels_count = serializers.SerializerMethodField()

    class Meta:
        model = campaigns_models.Product
        fields = (
            "id",
            "name",
            "sold_value",
            "remaining_value",
            "levels",
            "unlimited_levels_count",
        )

    def get_sold_value(self, obj: campaigns_models.Product) -> Decimal:
        """Calculate product's sold value from its levels."""
        return sum((level.sold_value for level in obj.prefetched_levels))

    def get_remaining_value(self, obj: campaigns_models.Product) -> Decimal:
        """Calculate product's remaining value from its levels."""
        return sum(
            (
                level.remaining_value
                for level in obj.prefetched_levels
                if level.remaining_value > 0
            )
        )

    def get_unlimited_levels_count(self, obj: campaigns_models.Product) -> int:
        """Calculate the number of unlimited levels in the product."""
        return len(
            [
                level
                for level in obj.prefetched_levels
                if level.amount < 0
            ],
        )


class ProductCategorySaleReportSerializer(ModelBaseSerializer):
    """Represent ProductCategory's sale report info."""

    products = ProductSaleReportSerializer(
        many=True,
        source="prefetched_products",
    )
    sold_value = serializers.SerializerMethodField()
    remaining_value = serializers.SerializerMethodField()
    unlimited_levels_count = serializers.SerializerMethodField()

    class Meta:
        model = campaigns_models.ProductCategory
        fields = (
            "id",
            "name",
            "sold_value",
            "remaining_value",
            "products",
            "unlimited_levels_count",
        )

    def get_sold_value(self, obj: campaigns_models.ProductCategory) -> Decimal:
        """Calculate category's sold value from its products."""
        return sum(
            (
                sum(
                    (
                        level.sold_value
                        for level in product.prefetched_levels
                    ),
                )
                for product in obj.prefetched_products
            ),
        )

    def get_remaining_value(
        self,
        obj: campaigns_models.ProductCategory,
    ) -> Decimal:
        """Calculate category's remaining value from its products."""
        return sum(
            (
                sum(
                    (
                        level.remaining_value
                        for level in product.prefetched_levels
                        if level.remaining_value > 0
                    ),
                )
                for product in obj.prefetched_products
            ),
        )

    def get_unlimited_levels_count(
        self,
        obj: campaigns_models.ProductCategory,
    ) -> int:
        """Calculate the number of unlimited levels in the category."""
        return sum(
            len(
                [
                    level
                    for level in product.prefetched_levels
                    if level.amount < 0
                ],
            )
            for product in obj.prefetched_products
        )


class SaleStatisticsReportSerializer(BaseSerializer):
    """Represent sale statistics data of a campaign."""

    total_sold_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    total_available_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    total_sold_count = serializers.IntegerField()
    total_available_count = serializers.IntegerField()

    class Meta:
        fields = (
            "total_sold_value",
            "total_available_value",
            "total_sold_count",
            "total_available_count",
        )

    def create(self, validated_data):
        """Bypass check."""

    def update(self, instance, validated_data):
        """Bypass check."""
