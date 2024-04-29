from rest_framework import serializers

from apps.core.api.serializers import ModelBaseSerializer
from apps.incentives.models import IncentiveQualifier


class IncentiveQualifierSerializer(ModelBaseSerializer):
    """Represent detail information of IncentiveQualifier."""

    class Meta:
        model = IncentiveQualifier
        fields = (
            "id",
            "name",
            "amount",
        )


class QualifierAmountListSerializer(serializers.Serializer):
    """Serializer for listing all of incentive qualifier amount."""

    value = serializers.IntegerField()
    label = serializers.CharField()

    class Meta:
        fields = (
            "value",
            "label",
        )

    def create(self, validated_data):
        """Bypass check."""

    def update(self, instance, validated_data):
        """Bypass check."""


class QualifierNameListSerializer(serializers.Serializer):
    """Serializer for listing all of incentive qualifier name."""

    value = serializers.CharField()
    label = serializers.CharField()

    class Meta:
        fields = (
            "value",
            "label",
        )

    def create(self, validated_data):
        """Bypass check."""

    def update(self, instance, validated_data):
        """Bypass check."""
