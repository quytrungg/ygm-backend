from django.db.models import Prefetch

from ordered_model.models import OrderedModelQuerySet
from safedelete.queryset import SafeDeleteQueryset

from apps.campaigns import models


class ProductQuerySet(SafeDeleteQueryset, OrderedModelQuerySet):
    """Provide custom queryset methods for Product."""

    def with_sale_report_data(self):
        """Prefetch levels with sale report data."""
        levels_prefetch = Prefetch(
            "levels",
            to_attr="prefetched_levels",
            queryset=models.Level.objects.all().with_sale_report_data(),
        )
        return self.prefetch_related(levels_prefetch)

    def for_duplication(self):
        """Prefetch data for duplication process."""
        levels_prefetch = Prefetch(
            "levels",
            queryset=(
                models.Level.objects.all().with_total_instances_count()
            ),
        )
        return self.prefetch_related(levels_prefetch, "attachments")
