from django_filters import rest_framework as filters


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    """Provide filtering based on multiple string values."""


class MultipleChoiceFilter(filters.BaseInFilter, filters.ChoiceFilter):
    """Filter class for filtering choices."""
