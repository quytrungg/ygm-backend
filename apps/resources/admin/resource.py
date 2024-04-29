from django import forms
from django.contrib import admin

from dal import autocomplete

from apps.core.admin import BaseAdmin

from ..models import Resource


class ResourceForm(forms.ModelForm):
    """Resource's form in django admin."""

    class Meta:
        model = Resource
        fields = "__all__"
        widgets = {
            "category": autocomplete.ModelSelect2(
                url="resource-category-autocomplete",
            ),
        }


@admin.register(Resource)
class ResourceAdmin(BaseAdmin):
    """Admin UI for Resource model."""

    ordering = (
        "name",
    )

    list_display = (
        "id",
        "name",
        "category",
    )
    list_display_links = (
        "id",
        "name",
        "category",
    )
    search_fields = (
        "id",
        "name",
        "category__name",
    )
    form = ResourceForm
