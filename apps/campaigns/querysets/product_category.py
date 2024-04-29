from django.db.models import Prefetch

from ordered_model.models import OrderedModelQuerySet
from safedelete.queryset import SafeDeleteQueryset

from apps.campaigns import models


class ProductCategoryQuerySet(SafeDeleteQueryset, OrderedModelQuerySet):
    """Provide custom queryset methods for ProductCategory."""

    def with_sale_report_data(self):
        """Prefetch products with sale report data."""
        products_prefetch = Prefetch(
            "products",
            to_attr="prefetched_products",
            queryset=models.Product.objects.all().with_sale_report_data(),
        )
        return self.prefetch_related(products_prefetch)
