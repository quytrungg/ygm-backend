from django.conf import settings

from rest_framework.permissions import BasePermission

from apps.users.models import User


def can_access_debug_tools(user: User) -> bool:
    """Return whether a user can access debug tools."""
    return user.is_superuser or not settings.RESTRICT_DEBUG_ACCESS


class HasAccessToDebugTools(BasePermission):
    """Permission for accessing debug tools."""

    def has_permission(self, request, view):
        """Check if the requesting user has access to debug tools."""
        return can_access_debug_tools(request.user)
