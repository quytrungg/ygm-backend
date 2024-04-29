from apps.core.autocomplete import AutocompleteView

from ..models import ResourceCategory


class ResourceCategoryAutocompleteView(AutocompleteView):
    """Provide autocomplete functionality."""

    queryset = ResourceCategory.objects.all()

    def get_queryset(self):
        """Return filtered queryset."""
        qs = super().get_queryset()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
