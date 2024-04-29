from rest_framework import serializers

from apps.core.api.serializers import ModelBaseSerializer

from ....models import Campaign


class CampaignSerializer(ModelBaseSerializer):
    """Serializer for Campaigns list, create, and detail for super admin."""

    status = serializers.ChoiceField(
        choices=Campaign.STATUSES.choices,
        default=Campaign.STATUSES.CREATED,
        required=False,
    )
    goal = serializers.DecimalField(
        decimal_places=2,
        max_digits=15,
        min_value=0,
        required=False,
        default=0,
    )

    class Meta:
        model = Campaign
        fields = (
            "id",
            "name",
            "status",
            "is_renewed",
            "year",
            "goal",
            "chamber",
        )
        extra_kwargs = {
            "chamber": {"required": True},
            "is_renewed": {"read_only": True},
        }
