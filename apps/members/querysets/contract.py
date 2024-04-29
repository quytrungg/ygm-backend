from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce

from safedelete.queryset import SafeDeleteQueryset


class ContractQuerySet(SafeDeleteQueryset):
    """Provide custom queryset methods for Contract."""

    def with_level_count(self):
        """Annotate number of levels added in the contract."""
        return self.annotate(
            levels_count=Count(
                "levels",
                filter=Q(levels__deleted_at__isnull=True),
            ),
        )

    def with_total_cost(self):
        """Annotate total cost of the contract."""
        return self.annotate(
            total_cost=Coalesce(
                Sum(
                    "levels__cost",
                    filter=Q(
                        levels__deleted_at__isnull=True,
                        levels__declined_at__isnull=True,
                    ),
                ),
                Decimal(0),
            ),
        )
