from rest_framework import serializers

from safedelete.config import HARD_DELETE

from apps.core.api.serializers import (
    BaseReorderSerializer,
    CurrentCampaignDefault,
    ModelBaseSerializer,
)
from apps.incentives.models import Incentive

from ....services.reward_services import create_new_rewards_for_volunteers
from .incentive_qualifier import IncentiveQualifierSerializer


class IncentiveWriteSerializer(ModelBaseSerializer):
    """Provide common fields for Incentive write and update operations."""

    qualifiers = IncentiveQualifierSerializer(many=True, required=False)
    campaign = serializers.HiddenField(
        default=CurrentCampaignDefault(),
        required=False,
    )

    class Meta:
        model = Incentive
        fields = (
            "id",
            "name",
            "threshold",
            "campaign",
            "value",
            "type",
            "qualifiers",
        )

    def create(self, validated_data):
        """Create an incentive with CA's chamber's campaign and qualifiers."""
        qualifiers = validated_data.pop("qualifiers", [])
        created_incentive = super().create(validated_data)

        for qualifier in qualifiers:
            qualifier["incentive"] = created_incentive

        qualifier_serializer = self.fields["qualifiers"]
        qualifier_serializer.create(qualifiers)
        campaign = validated_data["campaign"]
        create_new_rewards_for_volunteers(
            campaign_id=campaign.id,
            volunteer_ids=campaign.usercampaign_set.values_list(
                "id",
                flat=True,
            ),
        )
        return created_incentive

    def update(self, instance, validated_data):
        """Update an incentive with CA's chamber's campaign and qualifiers."""
        qualifiers = validated_data.pop("qualifiers", [])
        updated_incentive = super().update(instance, validated_data)
        updated_incentive.qualifiers.all().delete(force_policy=HARD_DELETE)

        for qualifier in qualifiers:
            qualifier["incentive"] = updated_incentive

        qualifier_serializer = self.fields["qualifiers"]
        qualifier_serializer.create(qualifiers)
        return updated_incentive


class BaseIncentiveReadSerializer(ModelBaseSerializer):
    """Provide common fields for Incentive read operations."""

    class Meta:
        model = Incentive
        fields = (
            "id",
            "name",
            "order",
            "threshold",
            "value",
            "type",
        )


class IncentiveDetailCASerializer(BaseIncentiveReadSerializer):
    """Provide common fields for Incentive detail operations."""

    qualifiers = IncentiveQualifierSerializer(many=True)

    class Meta(BaseIncentiveReadSerializer.Meta):
        fields = BaseIncentiveReadSerializer.Meta.fields + (
            "qualifiers",
        )


class IncentiveReorderSerializer(ModelBaseSerializer, BaseReorderSerializer):
    """Represent serializer to reorder incentives."""

    class Meta(BaseReorderSerializer.Meta):
        model = Incentive
