from apps.core.api.serializers import ModelBaseSerializer

from ....models import Level


class LevelCompactSerializer(ModelBaseSerializer):
    """Represent basic information of a Level."""

    class Meta:
        model = Level
        fields = (
            "id",
            "product_id",
            "name",
            "description",
            "benefits",
            "cost",
            "amount",
            "conditions",
        )
        extra_kwargs = {
            "cost": {"coerce_to_string": False},
        }
