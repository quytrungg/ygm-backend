from rest_framework import serializers

from apps.core.api.serializers import ModelBaseSerializer

from ....models import LevelInstance


class RecentlySoldLevelInstanceSerializer(ModelBaseSerializer):
    """Represent serializer for campaign dashboard in VS."""

    level_name = serializers.CharField(source="level.name")
    member_name = serializers.CharField(source="contract.member.name")
    date = serializers.DateTimeField(source="contract.approved_at")

    class Meta:
        model = LevelInstance
        fields = (
            "id",
            "level_name",
            "member_name",
            "date",
            "cost",
        )
