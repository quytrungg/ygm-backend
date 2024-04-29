from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field

from apps.core.api.serializers import ModelBaseSerializer
from apps.members.models import Member

from ....models import Level, Product, ProductCategory


class PurchasingMemberMarketingSerializer(ModelBaseSerializer):
    """Represent purchasing member data in marketing opportunities page."""

    class Meta:
        model = Member
        fields = (
            "id",
            "name",
        )


class LevelMarketingSerializer(ModelBaseSerializer):
    """Represent level data in marketing opportunities page."""

    total_instances_count = serializers.IntegerField()
    sold_instances_count = serializers.IntegerField()
    remaining_instances_count = serializers.SerializerMethodField()
    purchasing_members = serializers.SerializerMethodField()

    class Meta:
        model = Level
        fields = (
            "id",
            "name",
            "cost",
            "benefits",
            "total_instances_count",
            "sold_instances_count",
            "remaining_instances_count",
            "purchasing_members",
        )
        extra_kwargs = {
            "cost": {"coerce_to_string": False},
        }

    def get_remaining_instances_count(self, level: Level) -> int:
        """Return number of remaining instances of the `level`."""
        return level.total_instances_count - level.sold_instances_count

    @extend_schema_field(PurchasingMemberMarketingSerializer(many=True))
    def get_purchasing_members(self, level: Level):
        """Return level's purchasing members' information."""
        distinct_members = set(
            instance.contract.member for instance in level.instances.all()
        )
        return PurchasingMemberMarketingSerializer(
            distinct_members, many=True,
        ).data


class ProductMarketingSerializer(ModelBaseSerializer):
    """Represent product data in marketing opportunities page."""

    levels = LevelMarketingSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "levels",
        )


class ProductCategoryMarketingSerializer(ModelBaseSerializer):
    """Represent product category data in marketing opportunities page."""

    products = ProductMarketingSerializer(many=True)

    class Meta:
        model = ProductCategory
        fields = (
            "id",
            "name",
            "products",
        )
