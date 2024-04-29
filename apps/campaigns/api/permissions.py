from rest_framework.permissions import BasePermission

from apps.members.constants import ContractStatus

from ..models import LevelInstance, UserCampaign


class IsLevelInstanceEditable(BasePermission):
    """Check if a user is allowed to edit a level instance."""

    message = "Product is not editable."

    def has_object_permission(self, request, view, obj: LevelInstance) -> bool:
        """Allow request only when contract is not approved."""
        if obj.contract.status == ContractStatus.APPROVED:
            return False
        return super().has_object_permission(request, view, obj)


class IsUserCampaignDeletable(BasePermission):
    """Check if a `UserCampaign` can be deleted."""

    message = "Can't delete user with existing contracts."

    def has_object_permission(self, request, view, obj: UserCampaign):
        """Check if there's any contracts attached to the `UserCampaign`."""
        user_has_contracts = obj.created_contracts.all().exists()
        if user_has_contracts:
            return False
        return super().has_object_permission(request, view, obj)
