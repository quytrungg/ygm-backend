from django.db.models.functions import Collate

from apps.core.autocomplete import AutocompleteView

from ..models import Campaign


class CampaignAutocompleteView(AutocompleteView):
    """Provide autocomplete functionality."""

    queryset = Campaign.objects.all()

    def get_queryset(self):
        """Return filtered queryset."""
        qs = super().get_queryset()
        if self.q:
            qs = qs.annotate(
                name_deterministic=Collate("name", "und-x-icu"),
            ).filter(name_deterministic__icontains=self.q)
        return qs

    def get_search_fields(self):
        """Skip default search field."""
        return []
