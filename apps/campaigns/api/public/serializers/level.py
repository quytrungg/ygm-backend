import decimal
from functools import reduce
from operator import add

from django.db.models import FilteredRelation, Q, Sum

from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field, extend_schema_serializer

from apps.core.api.serializers import ModelBaseSerializer
from apps.members.constants import ContractStatus
from apps.members.models import Member

from ....models import Level


@extend_schema_serializer(component_name="LevelPublic")
class LevelSerializer(ModelBaseSerializer):
    """Represent information of a Level."""

    class Meta:
        model = Level
        fields = (
            "id",
            "product_id",
            "name",
            "cost",
            "benefits",
            "description",
            "conditions",
        )


class LevelPurchasingMemberSerializer(ModelBaseSerializer):
    """Represent information of Member purchasing a Level."""

    purchased_value = serializers.DecimalField(
        read_only=True,
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = Member
        fields = (
            "id",
            "name",
            "title",
            "purchased_value",
        )


class LevelDetailSerializer(ModelBaseSerializer):
    """Represent Level information to volunteer."""

    product_name = serializers.CharField(read_only=True, source="product.name")
    sold_instances_count = serializers.IntegerField(read_only=True)
    remaining_instances_count = serializers.IntegerField(read_only=True)
    members_purchased = serializers.SerializerMethodField()
    product_level_ids = serializers.SerializerMethodField()

    class Meta:
        model = Level
        fields = (
            "id",
            "name",
            "cost",
            "product_name",
            "sold_instances_count",
            "remaining_instances_count",
            "description",
            "benefits",
            "conditions",
            "members_purchased",
            "product_level_ids",
        )
        extra_kwargs = {
            "cost": {"coerce_to_string": False},
        }

    @extend_schema_field(LevelPurchasingMemberSerializer(many=True))
    def get_members_purchased(self, level: Level):
        """Return information about members purchasing the level."""
        members_purchased = Member.objects.annotate(
            approved_contracts=FilteredRelation(
                "contracts",
                condition=Q(
                    contracts__status=ContractStatus.APPROVED,
                    contracts__deleted_at__isnull=True,
                ),
            ),
            purchased_levels=FilteredRelation(
                "approved_contracts__levels",
                condition=Q(
                    approved_contracts__levels__declined_at__isnull=True,
                    approved_contracts__levels__deleted_at__isnull=True,
                ),
            ),
        ).filter(
            purchased_levels__level_id=level.id,
        ).annotate(
            purchased_value=Sum("purchased_levels__cost"),
        )
        return LevelPurchasingMemberSerializer(
            members_purchased, many=True,
        ).data

    def get_product_level_ids(self, level: Level) -> list[int]:
        """Return ids of levels of the same product as `level`'s product."""
        return Level.objects.filter(
            product_id=level.product_id,
        ).order_by("id").values_list("id", flat=True)


class MemberPurchasedLevelSerializer(ModelBaseSerializer):
    """Serializer for Level model of purchasing members."""

    product_name = serializers.CharField(source="product.name")
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Level
        fields = (
            "id",
            "name",
            "product_name",
            "amount",
        )

    def get_amount(self, level) -> decimal.Decimal:
        """Get total amount of levels purchased by member."""
        member_id = self.context["request"].query_params.get("member_id")
        return reduce(
            add,
            (
                instance.cost
                for instance in level.level_instances
                if str(instance.contract.member_id) == member_id
            ),
            decimal.Decimal(0),
        )
