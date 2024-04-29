from django.db import models

from django_filters import rest_framework as filters

from apps.core.api.filters import MultipleChoiceFilter
from apps.users.constants import UserRole

from ...constants import UserCampaignRole
from ...models import UserCampaign


class UserCampaignFilter(filters.FilterSet):
    """FilterSet for UserCampaign model."""

    role = MultipleChoiceFilter(
        choices=UserCampaignRole.choices,
    )
    exclude_role = MultipleChoiceFilter(
        method="exclude_user_with_roles",
        choices=UserCampaignRole.choices,
    )
    exclude_id = filters.NumberFilter(
        field_name="id",
        exclude=True,
    )
    member_id = filters.NumberFilter(
        field_name="member_id",
    )
    can_sell_contract = filters.BooleanFilter(
        method="filter_can_sell_contract",
    )

    class Meta:
        model = UserCampaign
        fields = (
            "role",
            "exclude_id",
            "member_id",
            "can_sell_contract",
        )

    # pylint: disable=unused-argument
    def exclude_user_with_roles(self, queryset, name, value):
        """Exclude user with specified roles."""
        if UserRole.CHAMBER_ADMIN in value:
            queryset = queryset.filter(
                ~models.Q(user__role=UserRole.CHAMBER_ADMIN),
            )
        return queryset.filter(
            ~models.Q(role__in=value),
        )

    def filter_can_sell_contract(self, queryset, name, value):
        """Filter users who can sell contract."""
        return queryset.with_can_sell_contract().filter(
            can_sell_contract=value,
        )
