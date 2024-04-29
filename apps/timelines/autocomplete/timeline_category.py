from apps.core.autocomplete import AutocompleteView

from ..models import TimelineCategory


class TimelineCategoryAutocompleteView(AutocompleteView):
    """Provide autocomplete functionality."""

    queryset = TimelineCategory.objects.all()

    def get_queryset(self):
        """Return filtered queryset."""
        qs = super().get_queryset()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
