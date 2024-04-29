from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field, extend_schema_serializer

from apps.core.api.serializers import ModelBaseSerializer
from apps.members.models import Member

from ....models import Level, Product
from ...common.serializers import ProductAttachmentSerializer


class MemberPurchasedProductSerializer(ModelBaseSerializer):
    """Represent information of Member purchasing a Level."""

    class Meta:
        model = Member
        fields = (
            "id",
            "name",
        )


class ProductLevelsSerializer(ModelBaseSerializer):
    """Represent level data nested in Product."""

    sold_instances_count = serializers.IntegerField()
    remaining_instances_count = serializers.IntegerField()

    class Meta:
        model = Level
        fields = (
            "id",
            "name",
            "cost",
            "sold_instances_count",
            "remaining_instances_count",
        )
        extra_kwargs = {
            "cost": {"coerce_to_string": False},
        }


@extend_schema_serializer(component_name="ListProductPublic")
class ListProductSerializer(ModelBaseSerializer):
    """Represent list of Product instances to volunteers."""

    attachments = ProductAttachmentSerializer(many=True, read_only=True)
    members_purchased = serializers.SerializerMethodField()
    levels = ProductLevelsSerializer(
        many=True,
        read_only=True,
        source="prefetch_levels",
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "attachments",
            "members_purchased",
            "levels",
        )

    @extend_schema_field(MemberPurchasedProductSerializer(many=True))
    def get_members_purchased(self, product: Product):
        """Return information of members purchasing the product."""
        members_purchased = set(
            instance.contract.member
            for level in product.prefetch_levels
            for instance in level.prefetch_instances
        )
        return MemberPurchasedProductSerializer(
            members_purchased,
            many=True,
        ).data
