from rest_framework import exceptions

from knox.auth import TokenAuthentication as KnoxTokenAuthentication

from apps.users import models as user_models
from apps.users.constants import UserRole


def get_chamber_id_from_header(request):
    """Return chamber id in request headers."""
    chamber_id = request.META.get("HTTP_CHAMBER", "")
    return chamber_id


class TokenAuthentication(KnoxTokenAuthentication):
    """Custom authentication class to support SA impersonation to CA."""

    def authenticate(self, request):
        """Authenticate the user.

        If user is Super admin, and chamber id is present in request headers,
        we treat it as an impersonation. The idea is replacing the returned
        SA user by CA user, so `request.user` will be CA user, while
        `request.auth` keeps the original token used for that request.

        """
        result = super().authenticate(request)
        if result is None:
            return None

        user, auth_token = result

        if user.role != UserRole.SUPER_ADMIN:
            return user, auth_token

        chamber_id = str(get_chamber_id_from_header(request=request))
        if not chamber_id:
            return user, auth_token

        msg = "Invalid token"
        if not chamber_id.isdigit():
            raise exceptions.AuthenticationFailed(msg)

        chamber_admin = user_models.User.objects.filter(
            role=UserRole.CHAMBER_ADMIN,
            chamber_id=chamber_id,
        ).first()
        if not chamber_admin:
            raise exceptions.AuthenticationFailed(msg)
        return chamber_admin, auth_token
