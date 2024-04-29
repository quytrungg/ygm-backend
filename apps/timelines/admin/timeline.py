from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from dal import autocomplete

from apps.core.admin import BaseAdmin

from ..models import Timeline


class TimelineForm(forms.ModelForm):
    """Timeline's form in django admin."""

    class Meta:
        model = Timeline
        fields = "__all__"
        widgets = {
            "created_by": autocomplete.ModelSelect2(url="user-autocomplete"),
            "chamber": autocomplete.ModelSelect2(url="chamber-autocomplete"),
            "category": autocomplete.ModelSelect2(
                url="timeline-category-autocomplete",
            ),
        }


@admin.register(Timeline)
class TimelineAdmin(BaseAdmin):
    """Admin UI for Timeline model."""

    list_display = (
        "id",
        "name",
        "order",
        "due_date",
        "status",
        "created_by",
        "assigned_to",
    )
    list_display_links = (
        "id",
        "name",
    )
    search_fields = (
        "name",
        "created_by__email",
        "assigned_to__email",
    )
    form = TimelineForm
    fieldsets = (
        (
            _("Task Info"),
            {
                "fields": (
                    "name",
                    "status",
                    "category",
                    "due_date",
                    "created_by",
                    "assigned_to",
                ),
            },
        ),
        (
            _("Task Details"),
            {
                "fields": (
                    "description",
                    "chamber",
                ),
            },
        ),
    )
