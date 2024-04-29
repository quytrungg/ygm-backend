from django import forms
from django.contrib import admin

from dal import autocomplete

from apps.core.admin import BaseAdmin

from ..models import Note


class NoteForm(forms.ModelForm):
    """Note's form in django admin."""

    class Meta:
        model = Note
        fields = "__all__"
        widgets = {
            "campaign": autocomplete.ModelSelect2(url="campaign-autocomplete"),
            "created_by": autocomplete.ModelSelect2(
                url="user-campaign-autocomplete",
            ),
            "modified_by": autocomplete.ModelSelect2(
                url="user-campaign-autocomplete",
            ),
        }


@admin.register(Note)
class NoteAdmin(BaseAdmin):
    """Admin UI for Note model."""

    ordering = (
        "campaign",
        "type",
    )
    list_display = (
        "id",
        "type",
        "campaign",
    )
    list_display_links = (
        "id",
        "type",
    )
    list_filter = ("type",)
    search_fields = ("body",)
    form = NoteForm
