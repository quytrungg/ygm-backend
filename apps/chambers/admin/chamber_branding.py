from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.core.admin import BaseAdmin

from ..models import ChamberBranding


@admin.register(ChamberBranding)
class ChamberBrandingAdmin(BaseAdmin):
    """Admin UI for ChamberBranding model."""

    list_display = (
        "id",
        "chamber",
        "headline",
    )
    list_display_links = (
        "id",
        "chamber",
        "headline",
    )
    search_fields = (
        "headline",
        "chamber__name",
    )
    fieldsets = (
        (
            _("Site Color"),
            {
                "fields": (
                    "site_primary_color",
                    "site_secondary_color",
                    "site_alternate_color",
                ),
            },
        ),
        (
            _("Logo"),
            {
                "fields": (
                    "chamber_logo",
                    "trc_logo",
                    "landing_bg",
                ),
            },
        ),
        (
            _("Others"),
            {
                "fields": (
                    "headline",
                    "public_prelaunch_msg",
                    "volunteer_prelaunch_msg",
                ),
            },
        ),
    )
