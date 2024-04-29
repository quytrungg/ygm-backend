from django import forms
from django.contrib import admin

from dal import autocomplete
from import_export_extensions.admin import CeleryImportExportMixin

from apps.core.admin import BaseAdmin

from ..models import StoredMember
from ..resources import StoredMemberResource


class StoredMemberForm(forms.ModelForm):
    """StoredMember's form in django admin."""

    class Meta:
        model = StoredMember
        fields = (
            "name",
            "chamber",
            "address",
            "city",
            "state",
            "zip",
            "phone",
        )
        widgets = {
            "chamber": autocomplete.ModelSelect2(url="chamber-autocomplete"),
        }


@admin.register(StoredMember)
class StoredMemberAdmin(CeleryImportExportMixin, BaseAdmin):
    """Admin UI for Stored Members."""

    list_display = (
        "id",
        "chamber",
        "name",
    )
    list_display_links = (
        "id",
        "chamber",
    )
    resource_class = StoredMemberResource
    form = StoredMemberForm
    search_fields = (
        "name",
    )
