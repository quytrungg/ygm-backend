from django_filters import rest_framework as filters

from ...models import Member


class PurchasingMemberFilter(filters.FilterSet):
    """FilterSet for Purchasing Member viewset."""

    created_by_id = filters.NumberFilter(
        field_name="contracts__created_by_id",
    )

    class Meta:
        model = Member
        fields = (
            "created_by_id",
        )
