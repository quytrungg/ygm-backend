from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from apps.campaigns.models import Level
from apps.members.models import Contract


class ContractTypeValidator:
    """Validate contract type with provided levels data."""

    requires_context = True

    def __call__(self, data: dict, serializer):
        """Ensure levels data satisfy contract type's constraints.

        If it's `cash` contract, no level should be traded.
        If it's `trade` contract, all levels should be traded.
        If campaign doesn't have trades, `trade` contract is not allowed.

        """
        contract_type = data["type"]
        campaign = getattr(serializer.context["request"], "campaign", None)
        if (
            not getattr(campaign, "has_trades", False)
            and contract_type == Contract.TYPES.TRADE
        ):
            raise serializers.ValidationError(
                {"type": _("Campaign does not allow trades")},
            )
        levels_data = data["levels"]
        trade_info = tuple(
            level_data["trade_with"] for level_data in levels_data
        )
        error = ""
        if contract_type == Contract.TYPES.CASH and any(trade_info):
            for level_data in levels_data:
                level_data["trade_with"] = ""
        elif contract_type == Contract.TYPES.TRADE and not all(trade_info):
            error = _(
                f"All levels of {Contract.TYPES.TRADE.label} contract must be "
                f"traded for something.",
            )

        if error:
            raise serializers.ValidationError({"type": error})


class ContractLevelsValidator:
    """Validate levels data during contract create/update."""

    requires_context = True

    def __call__(self, data: dict, serializer):
        """Ensure all selected level belong to user's current campaign."""
        levels_data = data["levels"]
        level_ids = [level_data["level_id"] for level_data in levels_data]
        campaign = serializer.root.context["request"].campaign
        level_count = Level.objects.filter(
            product__category__campaign_id=campaign.id,
            id__in=level_ids,
        ).count()
        if level_count != len(set(level_ids)):
            raise serializers.ValidationError(
                {
                    "levels": _("Invalid levels data."),
                },
            )
