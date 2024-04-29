from decimal import Decimal

from django.db import models
from django.db.models import F, functions

from ordered_model.models import OrderedModelQuerySet
from safedelete.queryset import SafeDeleteQueryset

from apps.members.constants import ContractStatus


class LevelQuerySet(SafeDeleteQueryset, OrderedModelQuerySet):
    """Provide custom queryset methods for Level."""

    # TODO: update total instances count logic
    def with_total_instances_count(self):
        """Annotate the total number of instances."""
        return self.annotate(total_instances_count=models.F("amount"))

    def with_sold_instances_count(self):
        """Annotate the number of sold instances.

        Sold instances are instances that meet following conditions:
            - attached to a contract
            - not declined
            - not soft-deleted

        """
        return self.annotate(
            sold_instances_count=models.Count(
                "instances",
                filter=models.Q(
                    instances__deleted_at__isnull=True,
                    instances__declined_at__isnull=True,
                    instances__contract_id__isnull=False,
                    instances__contract__status=ContractStatus.APPROVED,
                ),
            ),
        )

    def with_remaining_instances_count(self):
        """Annotate the number of available instances.

        Available instances are instances that meet following conditions:
            - not soft-deleted.
            - not attached to approved contract.

        """
        return (
            self
            .with_total_instances_count()
            .with_sold_instances_count()
            .annotate(
                remaining_instances_count=(
                    F("total_instances_count") - F("sold_instances_count")
                ),
            )
        )

    def with_available_amount(self):
        """Annotate the number of instances attachable to create contracts."""
        return self.with_sold_instances_count().annotate(
            available_amount=(
                models.F("amount") - models.F("sold_instances_count")
            ),
        )

    def with_sold_value(self):
        """Annotate the total value of sold instances.

        Sold instances are instances that meet following conditions:
            - attached to an approved contract
            - not declined
            - not soft-deleted

        """
        return self.annotate(
            sold_value=functions.Coalesce(
                models.Sum(
                    "instances__cost",
                    filter=models.Q(
                        instances__deleted_at__isnull=True,
                        instances__declined_at__isnull=True,
                        instances__contract_id__isnull=False,
                        instances__contract__status=ContractStatus.APPROVED,
                    ),
                ),
                Decimal(0),
            ),
        )

    def with_sale_report_data(self):
        """Annotate data for sale report."""
        return (
            self
            .with_total_instances_count()
            .with_sold_instances_count()
            .with_sold_value()
            .with_remaining_instances_count()
            .annotate(
                remaining_value=models.ExpressionWrapper(
                    F("remaining_instances_count") * F("cost"),
                    output_field=models.DecimalField(
                        max_digits=15,
                        decimal_places=2,
                    ),
                ),
            )
        )

    def with_is_available(self):
        """Annotate is_available field to indicate instance's attachable."""
        return self.with_available_amount().annotate(
            is_available=models.Case(
                models.When(available_amount=0, then=False),
                default=True,
            ),
        )
