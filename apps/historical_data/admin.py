from django.contrib import admin

from apps.core.admin import BaseAdmin
from apps.historical_data.models import DataImportJob, OldChamber


@admin.register(DataImportJob)
class DataImportJobAdmin(BaseAdmin):
    """Admin interface for import old data jobs."""

    list_display = (
        "id",
        "__str__",
        "target_chamber",
        "status",
    )

    fieldsets = (
        (
            None, {
                "fields": (
                    "job_kwargs",
                    "target_chamber",
                    "task_id",
                    "status",
                    "traceback",
                    "error_message",
                    "result",
                ),
            },
        ),
    )
    readonly_fields = (
        "task_id",
        "status",
        "traceback",
        "error_message",
        "result",
    )

    # pylint: disable=unused-argument
    def has_change_permission(self, request, *args, **kwargs):
        """Disable editing."""
        return False

    # pylint: disable=unused-argument
    def has_delete_permission(self, request, *args, **kwargs):
        """Disable deletion."""
        return False


@admin.register(OldChamber)
class OldChamberAdmin(BaseAdmin):
    """Admin interface for legacy chamber data."""

    search_fields = ("name",)
