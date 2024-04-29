from dal import autocomplete


class AutocompleteView(autocomplete.Select2QuerySetView):
    """Base class for autocomplete views."""

    def get_queryset(self):
        """Ensure user is authenticated, as recommended by docs."""
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        return qs
