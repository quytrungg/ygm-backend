from decimal import Decimal

from rest_framework import serializers

from libs.open_api.serializers import OpenApiSerializer

from apps.core.api.serializers import ModelBaseSerializer
from apps.members.models import Member


class PurchasingMemberSerializer(ModelBaseSerializer):
    """Serializer for purchasing members."""

    total_products = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = (
            "id",
            "name",
            "total_products",
            "total_spent",
        )

    def get_total_products(self, member) -> int:
        """Count total levels that member purchases."""
        contracts = member.member_contracts
        contract = contracts[0]
        return len(
            set(
                instance.level for instance in contract.member_instances
                if not instance.declined_at
            ),
        )

    def get_total_spent(self, member) -> Decimal:
        """Get total spent from a member."""
        contracts = member.member_contracts
        contract = contracts[0]
        return sum(
            instance.cost for instance in contract.member_instances
            if not instance.declined_at
        )


class MemberTotalEarningSerializer(OpenApiSerializer):
    """Represent serializer for purchasing members total earnings."""

    total_earnings = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        fields = (
            "total_earnings",
        )
