from django.db.models import Q

from apps.core.autocomplete import AutocompleteView

from ..models import User


class UserAutocompleteView(AutocompleteView):
    """Provide autocomplete functionality."""

    queryset = User.objects.all()

    def get_queryset(self):
        """Return filtered queryset."""
        qs = super().get_queryset()
        if self.q:
            qs = qs.filter(
                Q(first_name__icontains=self.q)
                | Q(last_name__icontains=self.q),
            )
        return qs

    def get_search_fields(self):
        """Skip default search field."""
        return []
