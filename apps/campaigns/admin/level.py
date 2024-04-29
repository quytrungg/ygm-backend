from django import forms
from django.contrib import admin

from dal import autocomplete
from import_export.forms import ExportForm

from apps.core.admin import BaseAdmin

from ..models import Campaign, Level


class LevelExportForm(ExportForm):
    """Provide filtering for exporting contracts."""

    campaign = forms.ModelChoiceField(
        queryset=Campaign.objects.all(),
        required=False,
        blank=True,
    )


class LevelForm(forms.ModelForm):
    """Level's form in django admin."""

    class Meta:
        model = Level
        fields = "__all__"
        widgets = {
            "product": autocomplete.ModelSelect2(url="product-autocomplete"),
        }


@admin.register(Level)
class LevelAdmin(BaseAdmin):
    """Admin UI for Level model."""

    ordering = (
        "name",
    )

    list_display = (
        "id",
        "name",
        "cost",
        "product",
    )
    list_display_links = (
        "id",
        "name",
    )
    search_fields = ("name",)
    readonly_fields = BaseAdmin.readonly_fields + (
        "external_id",
        "external_multiplier",
    )
    form = LevelForm
