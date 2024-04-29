import decimal

from rest_framework import serializers

from libs.open_api.serializers import OpenApiSerializer

from apps.campaigns.api.common.serializers import (
    LevelCompactSerializer,
    ProductCompactSerializer,
    UserCampaignCompactSerializer,
)
from apps.campaigns.models import LevelInstance, UserCampaign
from apps.core.api.serializers import ModelBaseSerializer
from apps.members.api.common.serializers import MemberReadSerializer

from ....models import Reward


class RallySessionWeekSerializer(OpenApiSerializer):
    """Represent week of rally session."""

    session_start = serializers.DateTimeField()
    session_end = serializers.DateTimeField()

    class Meta:
        fields = (
            "session_start",
            "session_end",
        )


class RewardSerializer(ModelBaseSerializer):
    """Represent detail information of Reward."""

    name = serializers.CharField(source="incentive.name")
    value = serializers.DecimalField(
        source="incentive.value",
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    type = serializers.CharField(source="incentive.type")

    class Meta:
        model = Reward
        fields = (
            "id",
            "name",
            "value",
            "type",
            "paid_at",
        )


class RallySessionUserCampaignSerializer(UserCampaignCompactSerializer):
    """Represent UserCampaign in rally session."""

    rewards = RewardSerializer(many=True)
    week_revenue = serializers.DecimalField(
        coerce_to_string=False,
        max_digits=15,
        decimal_places=2,
    )
    week_paid_reward_amount = serializers.DecimalField(
        coerce_to_string=False,
        max_digits=15,
        decimal_places=2,
    )

    class Meta(UserCampaignCompactSerializer.Meta):
        fields = UserCampaignCompactSerializer.Meta.fields + (
            "week_revenue",
            "week_paid_reward_amount",
            "rewards",
        )


class PaidAndOwedRewardSerializer(ModelBaseSerializer):
    """Serialize data for paid and owed rewards."""

    total_paid = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    total_owed = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    rewards = RewardSerializer(many=True)

    class Meta:
        model = UserCampaign
        fields = (
            "id",
            "first_name",
            "last_name",
            "total_paid",
            "total_owed",
            "rewards",
        )


class RewardMetricsSerializer(OpenApiSerializer):
    """Represent serializer to provide incentive metrics."""

    total_incentives = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    paid_incentives = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    owed_incentives = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        fields = (
            "total_incentives",
            "paid_incentives",
            "owed_incentives",
        )


class RewardMarkPaymentStatusSerializer(OpenApiSerializer):
    """Represent request data for reward mark payment status action."""

    id = serializers.IntegerField()
    is_paid = serializers.BooleanField()

    class Meta:
        fields = (
            "id",
            "is_paid",
        )


class PayoutMetricsSerializer(OpenApiSerializer):
    """Represent serializer to provide payout metrics for volunteers."""

    total_cash = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    total_trade = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    total_overall = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )
    total_paid = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        fields = (
            "total_cash",
            "total_trade",
            "total_overall",
            "total_paid",
        )


class RewardAccumulatingLevelSerializer(ModelBaseSerializer):
    """Represent Level info accumulating to a Reward."""

    cost = serializers.SerializerMethodField()
    level = LevelCompactSerializer()
    product = ProductCompactSerializer(source="level.product")
    approved_at = serializers.DateTimeField(
        source="contract.approved_at",
    )
    member = MemberReadSerializer(source="contract.member")

    class Meta:
        model = LevelInstance
        fields = (
            "id",
            "cost",
            "approved_at",
            "level",
            "product",
            "member",
        )

    def get_cost(self, level_instance: LevelInstance) -> decimal.Decimal:
        """Return the divided cost among volunteers."""
        return level_instance.cost * level_instance.credited_portion
