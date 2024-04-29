from rest_framework import serializers

from libs.open_api.serializers import OpenApiSerializer


class CampaignInventoryStatsSerializer(OpenApiSerializer):
    """Represent inventory's overall statistics."""

    total_value = serializers.DecimalField(
        decimal_places=2,
        max_digits=15,
        coerce_to_string=False,
    )
    levels_count = serializers.IntegerField()

    class Meta:
        fields = (
            "total_value",
            "levels_count",
        )
