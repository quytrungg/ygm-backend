from django.contrib import admin

from apps.core.admin import BaseAdmin

from ..models import TimelineAttachment


@admin.register(TimelineAttachment)
class TimelineAttachmentAdmin(BaseAdmin):
    """Admin UI for TimelineAttachment model."""

    list_display = (
        "id",
        "name",
        "content_type",
        "timeline",
    )
    list_display_links = (
        "id",
        "name",
    )
    search_fields = ("name",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "file",
                    "content_type",
                ),
            },
        ),
    )
