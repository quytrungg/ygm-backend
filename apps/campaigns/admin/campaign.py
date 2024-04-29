from django import forms
from django.contrib import admin
from django.db.models.functions import Collate
from django.utils.translation import gettext_lazy as _

from dal import autocomplete

from apps.core.admin import BaseAdmin

from ..models import Campaign


class CampaignForm(forms.ModelForm):
    """Campaign's form in django admin."""

    class Meta:
        model = Campaign
        fields = "__all__"
        widgets = {
            "chamber": autocomplete.ModelSelect2(url="chamber-autocomplete"),
        }


@admin.register(Campaign)
class CampaignAdmin(BaseAdmin):
    """Admin UI for Campaign model."""

    ordering = (
        "name",
    )

    list_display = (
        "id",
        "name",
        "status",
        "is_renewed",
        "year",
        "chamber",
    )
    list_display_links = (
        "id",
        "name",
        "status",
    )
    search_fields = (
        "name_deterministic",
    )
    form = CampaignForm
    fieldsets = (
        (
            _("Campaign Info"), {
                "fields": (
                    "name",
                    "status",
                    "is_renewed",
                ),
            },
        ),
        (
            _("Campaign Details"), {
                "fields": (
                    "year",
                    "timeline",
                    "goal",
                    "chamber",
                    "start_date",
                    "end_date",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        """Allow search by name."""
        return super().get_queryset(request).annotate(
            name_deterministic=Collate("name", "und-x-icu"),
        )
