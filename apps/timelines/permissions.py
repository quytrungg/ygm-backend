from rest_framework.permissions import BasePermission

from .constants import TimelineStatus


class IsTimelineIncomplete(BasePermission):
    """Block request if timeline is in `completed` status."""

    message = "Timeline is completed."

    def has_object_permission(self, request, view, obj):
        """Check if timeline is in `completed` status."""
        return obj.status != TimelineStatus.COMPLETED
