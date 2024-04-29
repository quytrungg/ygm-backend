from apps.campaigns.constants import UserCampaignRole
from apps.campaigns.models import Campaign, UserCampaign
from apps.members import services as members_services
from apps.members.models import ContractCreditInfo
from apps.users.constants import UserRole


def delete_user_campaign(user_campaign: UserCampaign):
    """Run user campaign deletion logic."""
    not_approved_shared_contracts = list(
        user_campaign.credited_contracts.filter(approved_at__isnull=True),
    )
    ContractCreditInfo.objects.filter(
        user_campaign=user_campaign,
        contract_id__in=[
            contract.id
            for contract in not_approved_shared_contracts
        ],
    ).delete()
    user_campaign.delete()
    for contract in not_approved_shared_contracts:
        members_services.redistribute_contract_credits(contract)


def create_default_user_campaign(campaign: Campaign):
    """Create default `UserCampaign` for chamber admins in new campaign."""
    chamber_admins = campaign.chamber.users.filter(role=UserRole.CHAMBER_ADMIN)
    user_campaigns = [
        UserCampaign(
            user=chamber_admin,
            campaign=campaign,
            first_name=chamber_admin.first_name,
            last_name=chamber_admin.last_name,
            email=chamber_admin.email,
            role=UserCampaignRole.VOLUNTEER,
        )
        for chamber_admin in chamber_admins
    ]
    UserCampaign.objects.bulk_create(user_campaigns)
