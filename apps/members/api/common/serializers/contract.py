from collections import OrderedDict

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

import safedelete
from drf_spectacular.utils import extend_schema_field

from apps.campaigns.api.chamber_admin.serializers import LevelSerializer
from apps.campaigns.api.common.serializers import UserCampaignCompactSerializer
from apps.campaigns.api.super_admin.serializers import CampaignSerializer
from apps.campaigns.models import Level, LevelInstance
from apps.chambers.api.serializers import ChamberCreateSASerializer
from apps.core.api.serializers import ModelBaseSerializer
from apps.members.models import Contract

from .member import MemberReadSerializer


class ContractListSerializer(ModelBaseSerializer):
    """Serializer for contracts with list method."""

    campaign = CampaignSerializer()
    levels_count = serializers.IntegerField()
    private_note = serializers.CharField()
    total_cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False,
    )
    member = MemberReadSerializer()
    created_by = UserCampaignCompactSerializer(read_only=True)

    class Meta:
        model = Contract
        fields = (
            "id",
            "name",
            "status",
            "private_note",
            "approved_at",
            "type",
            "member",
            "created_by",
            "campaign",
            "token",
            "levels_count",
            "total_cost",
            "signed_at",
        )


class ContractLevelSerializer(LevelSerializer):
    """Represent level serializer in contract without instances count."""

    amount = None

    class Meta:
        model = Level
        fields = (
            "id",
            "product",
            "name",
            "cost",
            "benefits",
            "description",
            "conditions",
        )
        extra_kwargs = {
            "cost": {"coerce_to_string": False},
        }


class ContractLevelInstanceSerializer(ModelBaseSerializer):
    """Serializer to retrieve LevelInstance model.

    This serializer is used in contract retrieve API.

    """

    level = ContractLevelSerializer()
    product_name = serializers.CharField(
        source="level.product.name",
        read_only=True,
    )

    class Meta:
        model = LevelInstance
        fields = (
            "id",
            "level",
            "cost",
            "declined_at",
            "trade_with",
            "product_name",
        )
        extra_kwargs = {
            "cost": {"coerce_to_string": False},
        }


class ContractPublicDetailSerializer(ContractListSerializer):
    """Serializer for contracts with retrieve method."""

    levels = serializers.SerializerMethodField()
    chamber = ChamberCreateSASerializer(source="campaign.chamber")
    shared_credits_with = serializers.SerializerMethodField()

    class Meta(ContractListSerializer.Meta):
        fields = ContractListSerializer.Meta.fields + (
            "chamber",
            "levels",
            "signed_at",
            "signature",
            "signer_ip_address",
            "shared_credits_with",
        )

    @extend_schema_field(ContractLevelInstanceSerializer(many=True))
    def get_levels(self, contract: Contract):
        """Return levels in correct order for error handling on FE."""
        return ContractLevelInstanceSerializer(
            contract.levels.order_by("id"),
            many=True,
        ).data

    @extend_schema_field(UserCampaignCompactSerializer(many=True))
    def get_shared_credits_with(self, contract: Contract):
        """Return only shared volunteers."""
        return UserCampaignCompactSerializer(
            contract.shared_credits_with.exclude(id=contract.created_by_id),
            many=True,
        ).data


class ContractLevelAttachMixin:
    """Mixin for attaching levels to contract."""

    # pylint: disable=too-many-locals
    def attach_levels_to_contract(
        self,
        contract: Contract,
        levels_data: list[dict],
    ):
        """Attach selected levels to the `contract`.

        IMPLEMENTATION EXPLANATION:
        - `id` field in each item of `levels_data` is id of `LevelInstance`
        attached to the contract. That means item with null `id` field are new
        selected level.
        - We acquire locks for all available `LevelInstance` of new selected
        levels to handle concurrency, and create a pool from them.
        - For each new selected level item in `levels_data`, we pop an instance
        out of the pool. If there's no available instances left, we raise error
        for that item.
        - Contract's instance is detached from contract if its `id`
        is not present in `levels_data`. Otherwise, its info is updated.

        """
        selected_levels_ids = {
            level_data["level_id"]: level_data
            for level_data in levels_data
        }
        contract.levels.exclude(
            id__in=[level_data["id"] for level_data in levels_data],
        ).delete(force_policy=safedelete.HARD_DELETE)

        contract_levels = contract.levels.all()
        contract_levels_map = {
            contract_level.id: contract_level
            for contract_level in contract_levels
        }
        new_instances = []
        updated_instances = []

        select_levels = Level.objects.filter(
            id__in=selected_levels_ids,
        ).with_available_amount()
        selected_levels_map = {
            level.id: level
            for level in select_levels
        }
        errors = OrderedDict()
        for idx, level_data in enumerate(levels_data):
            level = selected_levels_map[level_data["level_id"]]
            if level.available_amount == 0:
                errors[f"levels.{idx}.level_id"] = _(
                    "This product is out of stock",
                )
                continue
            level.available_amount -= 1
            if level_data["id"]:
                contract_level = contract_levels_map[level_data["id"]]
                contract_level.trade_with = level_data["trade_with"]
                updated_instances.append(contract_level)
                continue
            new_instance = LevelInstance.from_level(level)
            new_instance.contract = contract
            new_instance.trade_with = level_data["trade_with"]
            new_instances.append(new_instance)

        if errors:
            raise serializers.ValidationError(errors)

        LevelInstance.objects.bulk_update(
            updated_instances,
            fields=["trade_with"],
        )

        LevelInstance.objects.bulk_create(new_instances)
        return contract_levels


class ContractSelectedLevelSerializer(
    ContractLevelAttachMixin,
    ModelBaseSerializer,
):
    """Represent contract's selected levels in CREATE/UPDATE page."""

    id = serializers.IntegerField(required=True, allow_null=True)
    level = ContractLevelSerializer(read_only=True)
    level_id = serializers.IntegerField(required=True, write_only=True)
    product_name = serializers.CharField(
        source="level.product.name",
        read_only=True,
    )

    class Meta:
        model = LevelInstance
        fields = (
            "id",
            "level_id",
            "level",
            "trade_with",
            "cost",
            "declined_at",
            "product_name",
        )
        extra_kwargs = {
            "cost": {"read_only": True, "coerce_to_string": False},
            "declined_at": {"read_only": True},
            "trade_with": {"required": True},
        }
