from django_filters import rest_framework as filters

from apps.campaigns.models import Level, Product


class LevelFilter(filters.FilterSet):
    """FilterSet for Level model."""

    product = filters.ModelChoiceFilter(
        queryset=Product.objects.all(),
    )
    contract_attachable = filters.BooleanFilter(
        method="filter_by_availability",
    )

    class Meta:
        model = Level
        fields = (
            "product",
            "contract_attachable",
        )

    # pylint: disable=unused-argument
    def filter_by_availability(self, queryset, name, value):
        """Filter queryset by ability to be attached to contract."""
        return queryset.with_is_available().filter(is_available=value)


# pylint: disable=unused-argument
class MemberPurchasedLevelFilter(filters.FilterSet):
    """Filterset class for levels of purchasing member."""

    member_id = filters.NumberFilter(
        field_name="instances__contract__member_id",
    )

    class Meta:
        model = Level
        fields = (
            "member_id",
        )
