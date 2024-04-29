from rest_framework import serializers

from libs.open_api.serializers import OpenApiSerializer


class DashboardStatsSerializer(OpenApiSerializer):
    """Represent serializer for dashboard statistics in VS."""

    campaign_goal = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
        min_value=0,
        allow_null=True,
    )
    campaign_total = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
        min_value=0,
    )
    total_raised = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
        min_value=0,
    )
    personal_goal = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
        min_value=0,
        allow_null=True,
    )
    next_incentive_threshold = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
        min_value=0,
    )
    remaining_to_next_incentive = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
        min_value=0,
    )
    trip_incentive_threshold = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
        min_value=0,
    )
    remaining_to_trip_incentive = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
        min_value=0,
    )

    class Meta:
        fields = (
            "campaign_goal",
            "campaign_total",
            "total_raised",
            "personal_goal",
            "next_incentive_threshold",
            "remaining_to_next_incentive",
            "trip_incentive_threshold",
            "remaining_to_trip_incentive",
        )
