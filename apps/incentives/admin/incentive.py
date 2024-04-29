from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from dal import autocomplete

from apps.core.admin import BaseAdmin

from ..models import Incentive


class IncentiveForm(forms.ModelForm):
    """Incentive's form in django admin."""

    class Meta:
        model = Incentive
        fields = "__all__"
        widgets = {
            "campaign": autocomplete.ModelSelect2(url="campaign-autocomplete"),
        }


@admin.register(Incentive)
class IncentiveAdmin(BaseAdmin):
    """Admin UI for Incentive model."""

    list_display = (
        "id",
        "name",
        "order",
        "threshold",
        "value",
        "type",
        "campaign_id",
    )
    list_display_links = (
        "id",
        "name",
    )
    search_fields = (
        "name",
        "campaign__name",
    )
    form = IncentiveForm
    fieldsets = (
        (
            _("Incentive Info"),
            {
                "fields": (
                    "name",
                ),
            },
        ),
        (
            _("Incentive Details"),
            {
                "fields": (
                    "threshold",
                    "value",
                    "type",
                ),
            },
        ),
        (
            _("Campaign Info"),
            {
                "fields": (
                    "campaign",
                ),
            },
        ),
    )
