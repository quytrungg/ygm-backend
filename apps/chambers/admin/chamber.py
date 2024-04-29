from django.contrib import admin
from django.db.models.functions import Collate
from django.utils.translation import gettext_lazy as _

from apps.core.admin import BaseAdmin

from ..models import Chamber


@admin.register(Chamber)
class ChamberAdmin(BaseAdmin):
    """Admin UI for Chamber model."""

    list_display = (
        "id",
        "name",
        "nickname",
        "subdomain",
        "can_renew_campaign",
    )
    list_display_links = (
        "id",
        "name",
        "nickname",
    )
    search_fields = (
        "name",
        "nickname_deterministic",
    )
    fieldsets = (
        (
            _("Main Info"),
            {
                "fields": (
                    "name",
                    "nickname",
                    "subdomain",
                ),
            },
        ),
        (
            _("Contact Info"),
            {
                "fields": (
                    "address",
                    "city",
                    "state",
                    "zipcode",
                    "country",
                    "phone",
                ),
            },
        ),
        (
            _("Mail Info"),
            {
                "fields": (
                    "mail_address",
                    "mail_city",
                    "mail_state",
                    "mail_zipcode",
                    "mail_country",

                ),
            },
        ),
        (
            _("TRC Coordinator Info"),
            {
                "fields": (
                    "trc_coord_first_name",
                    "trc_coord_last_name",
                    "trc_coord_email",
                    "trc_coord_phone",
                    "trc_coord_title",
                    "trc_coord_office_phone",
                    "trc_coord_office_phone_ext",
                    "pre_income",
                ),
            },
        ),
        (
            _("CEO Info"),
            {
                "fields": (
                    "ceo_first_name",
                    "ceo_last_name",
                    "ceo_email",
                    "ceo_phone",
                ),
            },
        ),
        (
            _("Social Info"),
            {
                "fields": (
                    "instagram_url",
                    "facebook_url",
                    "twitter_url",
                    "youtube_url",
                    "linkedin_url",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        """Support search on nickname field."""
        return super().get_queryset(request).annotate(
            nickname_deterministic=Collate("nickname", "und-x-icu"),
        )
