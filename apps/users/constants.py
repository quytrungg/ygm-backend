from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class UserRole(TextChoices):
    """Possible User Roles."""

    SUPER_ADMIN = "super_admin", _("Super Admin")
    CHAMBER_ADMIN = "chamber_admin", _("Chamber Admin")
    CHAMBER_CHAIR = "chamber_chair", _("Chamber Chair")
    VICE_CHAIR = "vice_chair", _("Vice Chair")
    TEAM_CAPTAIN = "team_captain", _("Team Captain")
    VOLUNTEER = "volunteer", _("Volunteer")


VOLUNTEER_PERMISSIONS = (
    UserRole.VOLUNTEER.value,
)

TEAM_CAPTAIN_PERMISSIONS = (
    UserRole.TEAM_CAPTAIN.value,
) + VOLUNTEER_PERMISSIONS

VICE_CHAIR_PERMISSIONS = (
    UserRole.VICE_CHAIR.value,
) + TEAM_CAPTAIN_PERMISSIONS

CHAMBER_CHAIR_PERMISSIONS = (
    UserRole.CHAMBER_CHAIR.value,
) + VICE_CHAIR_PERMISSIONS


CHAMBER_ADMIN_PERMISSIONS = (
    UserRole.CHAMBER_ADMIN.value,
) + CHAMBER_CHAIR_PERMISSIONS


SUPER_ADMIN_PERMISSIONS = (
    UserRole.SUPER_ADMIN.value,
) + CHAMBER_ADMIN_PERMISSIONS


USER_ROLE_PERMISSIONS_MAP = {
    UserRole.VOLUNTEER.value: VOLUNTEER_PERMISSIONS,
    UserRole.TEAM_CAPTAIN.value: TEAM_CAPTAIN_PERMISSIONS,
    UserRole.VICE_CHAIR.value: VICE_CHAIR_PERMISSIONS,
    UserRole.CHAMBER_CHAIR.value: CHAMBER_CHAIR_PERMISSIONS,
    UserRole.CHAMBER_ADMIN.value: CHAMBER_ADMIN_PERMISSIONS,
    UserRole.SUPER_ADMIN.value: SUPER_ADMIN_PERMISSIONS,
}
