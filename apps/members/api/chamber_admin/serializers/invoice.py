from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field

from apps.campaigns.models import LevelInstance, Product
from apps.campaigns.utils import get_chamber_url
from apps.chambers.api.serializers import InvoiceChamberSerializer
from apps.core.api.serializers import ModelBaseSerializer
from apps.members import models

from ...common.serializers import MemberReadSerializer


class InvoiceProductSerializer(ModelBaseSerializer):
    """Represent product info in invoice."""

    category_name = serializers.CharField(source="category.name")

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "category_name",
        )


class InvoiceLevelInstanceSerializer(ModelBaseSerializer):
    """Represent level instance info in invoice."""

    name = serializers.CharField(source="level.name")
    cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    product = InvoiceProductSerializer(source="level.product")

    class Meta:
        model = LevelInstance
        fields = (
            "id",
            "name",
            "cost",
            "product",
        )


class InvoiceDetailSerializer(ModelBaseSerializer):
    """Represent Invoice's detail information."""

    member = MemberReadSerializer(source="contract.member")
    levels = serializers.SerializerMethodField()
    chamber = InvoiceChamberSerializer(source="contract.campaign.chamber")
    contract_public_url = serializers.SerializerMethodField()

    class Meta:
        model = models.Invoice
        fields = (
            "id",
            "name",
            "status",
            "levels",
            "member",
            "chamber",
            "is_paid",
            "contract_public_url",
            "sent_at",
            "created",
        )

    @extend_schema_field(InvoiceLevelInstanceSerializer(many=True))
    def get_levels(self, invoice: models.Invoice) -> list[dict]:
        """Return levels purchased in contract for invoice."""
        levels = invoice.contract.levels.filter(
            deleted_at__isnull=True,
            declined_at__isnull=True,
        )
        return InvoiceLevelInstanceSerializer(levels, many=True).data

    def get_contract_public_url(self, invoice: models.Invoice) -> str:
        """Return the contract's public url."""
        chamber_url = get_chamber_url(invoice.contract.campaign.chamber)
        return f"{chamber_url}/contract-sign?token={invoice.contract.token}"


class ListInvoiceSerializer(ModelBaseSerializer):
    """Represent list of invoices."""

    status = serializers.ChoiceField(
        choices=models.Invoice.STATUSES,
        read_only=True,
    )
    contract_name = serializers.CharField(read_only=True)
    cost = serializers.DecimalField(
        read_only=True,
        coerce_to_string=False,
        max_digits=15,
        decimal_places=2,
    )
    levels_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Invoice
        fields = (
            "id",
            "status",
            "contract_name",
            "cost",
            "levels_count",
        )
