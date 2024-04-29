from django import forms
from django.contrib import admin

from dal import autocomplete

from apps.core.admin import BaseAdmin

from ..models import ResourceCategory


class ResourceCategoryForm(forms.ModelForm):
    """ResourceCategory's form in django admin."""

    class Meta:
        model = ResourceCategory
        fields = "__all__"
        widgets = {
            "chamber": autocomplete.ModelSelect2(
                url="chamber-autocomplete",
            ),
        }


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(BaseAdmin):
    """Admin UI for ResourceCategory model."""

    ordering = (
        "name",
    )

    list_display = (
        "id",
        "name",
    )
    list_display_links = (
        "id",
        "name",
    )
    search_fields = (
        "id",
        "name",
    )
    form = ResourceCategoryForm
