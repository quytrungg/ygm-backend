from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from libs.open_api.serializers import OpenApiSerializer

from apps.campaigns.models import LevelInstance, UserCampaign
from apps.core.api.serializers import BaseSerializer, ModelBaseSerializer
from apps.members.models import Contract

from .... import services
from ...common.serializers import (
    ContractLevelAttachMixin,
    ContractSelectedLevelSerializer,
)
from ...common.validators import ContractLevelsValidator, ContractTypeValidator


class ContractApproveSerializer(OpenApiSerializer, BaseSerializer):
    """Represent body of contract approval request."""

    selected_level_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )

    class Meta:
        fields = (
            "selected_level_ids",
        )

    def validate(self, attrs):
        """Validate contract's levels' availability."""
        contract = self.instance
        LevelInstance.objects.filter(
            contract=contract,
            declined_at__isnull=True,
        ).exclude(id__in=attrs["selected_level_ids"]).update(
            declined_at=timezone.now(),
        )
        errors = services.validate_available_levels(
            LevelInstance.objects.filter(
                contract=contract,
                declined_at__isnull=True,
            ).annotate(
                index=models.Case(
                    *[
                        models.When(id=instance.id, then=idx)
                        for idx, instance in enumerate(
                            contract.levels.order_by("id"),
                        )
                    ],
                    output_field=models.IntegerField(),
                ),
            ),
        )
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def save(self, **kwargs):
        """Approve the contract."""
        services.approve_contract(self.instance)


class ContractReassignSerializer(OpenApiSerializer):
    """Represent serializer to reassign contracts."""

    contract = serializers.PrimaryKeyRelatedField(
        queryset=Contract.objects.all().prefetch_related("credits_info"),
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=UserCampaign.objects.all().can_sell_contract(),
    )

    class Meta:
        fields = (
            "contract",
            "user",
        )


class ContractEditCreditsSerializer(ModelBaseSerializer):
    """Handle contract credits edit logic."""

    shared_credits_with = serializers.PrimaryKeyRelatedField(
        queryset=UserCampaign.objects.all(),
        many=True,
    )

    class Meta:
        model = Contract
        fields = (
            "id",
            "shared_credits_with",
        )

    def validate(self, attrs: dict) -> dict:
        """Check if contract credits can be edited and valid."""
        contract: Contract = self.instance
        if contract.status != Contract.STATUSES.SIGNED:
            raise serializers.ValidationError(
                _("Contract credits can only be edited in Signed status"),
            )
        invalid_shared_users = services.get_contract_invalid_shared_volunteers(
            contract_creator=contract.created_by,
            shared_volunteers=attrs["shared_credits_with"],
            contract_stored_member_id=contract.member.stored_member_id,
        )
        if invalid_shared_users:
            raise serializers.ValidationError(
                {"shared_credits_with": _("Invalid shared credits info")},
            )
        return attrs


class ContractUpdateSerializer(ContractLevelAttachMixin, ModelBaseSerializer):
    """Handle the update of `type` field of contract."""

    levels = ContractSelectedLevelSerializer(many=True)

    class Meta:
        model = Contract
        fields = (
            "id",
            "type",
            "levels",
        )
        validators = [ContractTypeValidator(), ContractLevelsValidator()]

    def update(self, instance, validated_data):
        """Update contract type and corresponding levels if needed."""
        levels_data = validated_data.pop("levels")
        updated_contract = super().update(instance, validated_data)
        self.attach_levels_to_contract(updated_contract, levels_data)
        return updated_contract
