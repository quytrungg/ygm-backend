from django_filters import rest_framework as filters

from apps.campaigns.models import Product, ProductCategory


class ProductFilter(filters.FilterSet):
    """FilterSet for Product model."""

    category = filters.ModelChoiceFilter(
        queryset=ProductCategory.objects.all(),
    )

    class Meta:
        model = Product
        fields = (
            "category",
        )
