from rest_framework.permissions import BasePermission

from apps.campaigns.constants import CampaignStatus
from apps.members.constants import ContractStatus


class IsDraftContract(BasePermission):
    """Ensure CA and SA can only delete draft contracts."""

    message = "Contract is editable in draft mode only."

    def has_object_permission(self, request, view, obj) -> bool:
        """Check if contract's status is `draft`."""
        return obj.status == ContractStatus.DRAFT


class IsSignableContract(BasePermission):
    """Ensure users cannot sign to signed contract."""

    message = "Contract can't be signed."

    def has_object_permission(self, request, view, obj) -> bool:
        """Check if contract is still available to be signed."""
        return (
            obj.status == ContractStatus.SENT
            and obj.signature == ""
            and obj.signed_at is None
        )


class IsContractCampaignLiveOrRenewal(BasePermission):
    """Ensure users only access to contracts with `live`/`renewal` campaign."""

    message = "Campaign is not active yet."

    def has_object_permission(self, request, view, obj):
        """Check if contract's campaign is in live status."""
        return obj.campaign.status in (
            CampaignStatus.LIVE,
            CampaignStatus.RENEWAL,
        )
