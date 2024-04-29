from django.contrib import admin

from apps.core.admin import BaseAdmin

from ..models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(BaseAdmin):
    """Admin UI for Invoice model."""

    list_display = (
        "id",
        "contract",
        "is_paid",
        "sent_at",
    )
    list_display_links = (
        "id",
    )
    create_only_fields = ("contract",)
    search_fields = ("contract__name",)
