from apps.core.api.serializers import ModelBaseSerializer

from ....models import Product


class ProductCompactSerializer(ModelBaseSerializer):
    """Represent basic information of a Product."""

    class Meta:
        model = Product
        fields = (
            "id",
            "category_id",
            "name",
            "description",
        )
