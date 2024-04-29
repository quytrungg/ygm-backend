from django import forms
from django.contrib import admin

from dal import autocomplete

from apps.core.admin import BaseAdmin

from ..models import Team


class TeamForm(forms.ModelForm):
    """Team's form in django admin."""

    class Meta:
        model = Team
        fields = "__all__"
        widgets = {
            "campaign": autocomplete.ModelSelect2(url="campaign-autocomplete"),
            "managed_by": autocomplete.ModelSelect2(
                url="user-campaign-autocomplete",
            ),
        }


@admin.register(Team)
class TeamAdmin(BaseAdmin):
    """Admin ui for Team model."""

    ordering = (
        "name",
    )

    list_display = (
        "id",
        "name",
        "campaign",
    )
    search_fields = ("name",)
    form = TeamForm
