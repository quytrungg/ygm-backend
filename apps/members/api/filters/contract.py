from django.core.exceptions import FieldError

from django_filters import rest_framework as filters
from drf_spectacular import drainage

from libs.open_api.filters import OrderingFilterBackend

from apps.core.api.filters import MultipleChoiceFilter

from ...models import Contract


class ContractFilter(filters.FilterSet):
    """FilterSet for Contract model."""

    statuses = MultipleChoiceFilter(
        field_name="status",
        choices=Contract.STATUSES.choices,
    )
    is_renewed = filters.BooleanFilter(field_name="is_renewed")

    class Meta:
        model = Contract
        fields = (
            "statuses",
            "is_renewed",
            "created_by_id",
        )


class ContractOrderingFilterBackend(OrderingFilterBackend):
    """Custom backend for Contract list API."""

    def remove_invalid_fields(self, queryset, fields, view, request):
        """Remove invalid fields from ordering fields."""
        valid_fields: list[str] = super().remove_invalid_fields(
            queryset,
            fields,
            view,
            request,
        )
        valid_fields = self.replace_approval_priority_field(valid_fields)
        return valid_fields

    def replace_approval_priority_field(self, ordering_fields) -> list[str]:
        """Replace `approval_priority` field with its constituent fields."""
        approval_priority_field = "approval_priority"
        for idx, field in enumerate(ordering_fields):
            if field == approval_priority_field:
                return (
                    ordering_fields[:idx]
                    + ["-status_priority_for_approval", "signed_at"]
                    + ordering_fields[idx + 1:]
                )
            if field == f"-{approval_priority_field}":
                return (
                    ordering_fields[:idx]
                    + ["status_priority_for_approval", "-signed_at"]
                    + ordering_fields[idx + 1:]
                )
        return ordering_fields

    def _validate_ordering_fields(self, view):
        """Validate `ordering_fields` in view."""
        try:
            view.get_queryset().order_by(
                *self.replace_approval_priority_field(
                    list(view.ordering_fields),
                ),
            )
        except FieldError as error:
            drainage.warn(
                "`ordering_fields` contains non-existent"
                " or non-related fields."
                f" {error}",
            )
