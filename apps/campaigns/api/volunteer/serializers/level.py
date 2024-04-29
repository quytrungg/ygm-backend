from rest_framework import serializers

from apps.core.api.serializers import ModelBaseSerializer

from ....models import Level


class RemainingSponsorshipSerializer(ModelBaseSerializer):
    """Represent serializer for remaining sponsorship API."""

    product_name = serializers.CharField()
    sold_instances_count = serializers.IntegerField()
    remaining_instances_count = serializers.IntegerField()
    category_id = serializers.IntegerField(source="product.category_id")

    class Meta:
        model = Level
        fields = (
            "id",
            "name",
            "cost",
            "product_id",
            "category_id",
            "product_name",
            "sold_instances_count",
            "remaining_instances_count",
        )
