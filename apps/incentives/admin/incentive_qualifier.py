from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.core.admin import BaseAdmin

from ..models import IncentiveQualifier


@admin.register(IncentiveQualifier)
class IncentiveQualifierAdmin(BaseAdmin):
    """Admin UI for IncentiveQualifier model."""

    list_display = (
        "id",
        "name",
        "amount",
        "incentive",
    )
    list_display_links = (
        "id",
        "name",
    )
    search_fields = (
        "name",
        "incentive__name",
    )
    fieldsets = (
        (
            _("Incentive Qualifier Info"),
            {
                "fields": (
                    "name",
                    "amount",
                ),
            },
        ),
        (
            _("Incentive Info"),
            {
                "fields": (
                    "incentive",
                ),
            },
        ),
    )
