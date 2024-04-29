from django import forms
from django.contrib import admin

from dal import autocomplete
from import_export.forms import ExportForm

from apps.campaigns.models import Campaign
from apps.core.admin import BaseAdmin

from ..models import Contract


class ContractExportForm(ExportForm):
    """Provide filtering for exporting contracts."""

    campaign = forms.ModelChoiceField(
        queryset=Campaign.objects.all(),
        required=False,
        blank=True,
    )


class ContractForm(forms.ModelForm):
    """Contract's form in django admin."""

    class Meta:
        model = Contract
        fields = "__all__"
        widgets = {
            "member": autocomplete.ModelSelect2(url="member-autocomplete"),
            "campaign": autocomplete.ModelSelect2(url="campaign-autocomplete"),
            "created_by": autocomplete.ModelSelect2(
                url="user-campaign-autocomplete",
            ),
        }


@admin.register(Contract)
class ContractAdmin(BaseAdmin):
    """Admin UI for Contract model."""

    ordering = (
        "status",
    )
    list_display = (
        "id",
        "name",
        "status",
        "approved_at",
    )
    list_display_links = (
        "id",
        "name",
    )
    search_fields = ("name",)
    form = ContractForm
    fieldsets = (
        (
            None, {
                "fields": (
                    "type",
                    "status",
                    "note",
                    "approved_at",
                    "created_by",
                    "member",
                    "campaign",
                    "token",
                    "signature",
                    "signed_at",
                    "is_renewed",
                ),
            },
        ),
    )
    readonly_fields = (
        "token",
    )
