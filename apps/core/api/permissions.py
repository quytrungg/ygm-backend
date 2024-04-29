from rest_framework.permissions import BasePermission, IsAuthenticated

from apps.campaigns.constants import CampaignStatus, UserCampaignRole
from apps.users.constants import UserRole


class IsVolunteer(BasePermission):
    """Allow Volunteer to perform actions."""

    def has_permission(self, request, view):
        """Allow if user is Volunteer."""
        return self._is_volunteer(request.user)

    def has_object_permission(self, request, view, obj):
        """Allow if user is Volunteer."""
        return self._is_volunteer(request.user)

    @staticmethod
    def _is_volunteer(user) -> bool:
        """Check if user is Volunteer."""
        return user.role == UserRole.VOLUNTEER


class IsChamberChair(BasePermission):
    """Allow Chamber chair to perform actions."""

    def has_permission(self, request, view):
        """Allow if user is campaign's chair."""
        campaign = getattr(request, "campaign", None)
        if not self._is_chamber_chair(request.user, campaign):
            return False
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """Allow if user is campaign's chair."""
        campaign = getattr(request, "campaign", None)
        if not self._is_chamber_chair(request.user, campaign):
            return False
        return super().has_object_permission(request, view, obj)

    @staticmethod
    def _is_chamber_chair(user, campaign) -> bool:
        """Check if user has chair role in campaign."""
        if not campaign:
            return False
        user_campaign = user.user_campaigns.filter(campaign=campaign).first()
        if not user_campaign:
            return False
        return user_campaign.role == UserCampaignRole.CHAMBER_CHAIR


class AllowAllRoles(IsAuthenticated):
    """Allow all users to access endpoint."""

    allowed_roles = (
        UserRole.SUPER_ADMIN.value,
        UserRole.CHAMBER_ADMIN.value,
        UserRole.CHAMBER_CHAIR.value,
        UserRole.VICE_CHAIR.value,
        UserRole.TEAM_CAPTAIN.value,
        UserRole.VOLUNTEER.value,
    )

    def has_permission(self, request, view):
        """Allow access to users wits allowed roles."""
        if super().has_permission(request, view):
            return request.user.role in self.allowed_roles
        return False


class AllowAdmin(AllowAllRoles):
    """Allow Super Admin users to access endpoint."""

    allowed_roles = (
        UserRole.SUPER_ADMIN,
    )


class AllowChamberAdmin(AllowAllRoles):
    """Allow Super and Chamber Admins users to access endpoint."""

    allowed_roles = (
        UserRole.SUPER_ADMIN,
        UserRole.CHAMBER_ADMIN,
    )


class AllowChamberUser(AllowAllRoles):
    """Allow users who belong to a specific chamber."""

    allowed_roles = (
        UserRole.CHAMBER_ADMIN,
        UserRole.VOLUNTEER,
    )


class CampaignStatusPermission(BasePermission):
    """Block requests if campaign is not in a certain state."""

    allowed_statuses = tuple()

    def has_permission(self, request, view) -> bool:
        """Allow requests only if campaign is in a certain state."""
        campaign = getattr(request, "campaign", None)
        if not campaign or campaign.status not in self.allowed_statuses:
            return False
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj) -> bool:
        """Allow requests only if campaign is in a certain state."""
        campaign = getattr(request, "campaign", None)
        if not campaign or campaign.status not in self.allowed_statuses:
            return False
        return super().has_object_permission(request, view, obj)


class IsCampaignOpen(CampaignStatusPermission):
    """Block requests if campaign is not in `created` state."""

    allowed_statuses = (CampaignStatus.CREATED, CampaignStatus.RENEWAL)


class IsCampaignLive(CampaignStatusPermission):
    """Block requests if campaign is not in `live` state."""

    allowed_statuses = (CampaignStatus.LIVE,)


class IsCampaignRenewal(CampaignStatusPermission):
    """Block requests if campaign is not in `renewal` state."""

    allowed_statuses = (CampaignStatus.RENEWAL,)


IsCampaignInProgress = IsCampaignOpen | IsCampaignLive
