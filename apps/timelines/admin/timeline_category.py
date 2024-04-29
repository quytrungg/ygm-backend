from django.contrib import admin

from apps.core.admin import BaseAdmin

from ..models import TimelineCategory


@admin.register(TimelineCategory)
class TimelineCategoryAdmin(BaseAdmin):
    """Admin UI for TimelineCategory model."""

    list_display = (
        "id",
        "name",
    )
    list_display_links = (
        "id",
        "name",
    )
    search_fields = (
        "name",
    )
    fieldsets = (
        (
            None, {
                "fields": (
                    "name",
                ),
            },
        ),
    )
