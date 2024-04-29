from rest_framework import serializers

from apps.core.api.serializers import ModelBaseSerializer
from apps.members.models import Contract

from ....models import Level, LevelInstance


class LevelInstanceSerializer(ModelBaseSerializer):
    """Serializer for chamber admin to manage LevelInstance model."""

    level = serializers.PrimaryKeyRelatedField(queryset=Level.objects.all())
    contract = serializers.PrimaryKeyRelatedField(
        queryset=Contract.objects.all(),
    )
    cost = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0,
        required=True,
        coerce_to_string=False,
    )
    is_declined = serializers.SerializerMethodField()

    class Meta:
        model = LevelInstance
        fields = (
            "level",
            "contract",
            "cost",
            "is_declined",
        )

    def get_is_declined(self, obj: LevelInstance) -> bool:
        """Return true if level instance is declined, false otherwise."""
        return bool(obj.declined_at)


class LevelInstanceUpdateSerializer(ModelBaseSerializer):
    """Serializer for LevelInstance model to update cost."""

    cost = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0,
        required=True,
        coerce_to_string=False,
    )

    class Meta:
        model = LevelInstance
        fields = (
            "cost",
        )
