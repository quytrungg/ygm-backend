from typing import Iterable

from apps.campaigns.models import Campaign
from apps.chambers.models import Chamber, StoredMember
from apps.historical_data.services import connection
from apps.historical_data.services.chambers import import_chambers
from apps.historical_data.services.contracts import import_contracts
from apps.historical_data.services.incentives import import_chamber_incentives
from apps.historical_data.services.inventory import import_chamber_inventory
from apps.historical_data.services.resources import import_chamber_resources
from apps.historical_data.services.rewards import import_chamber_rewards
from apps.historical_data.services.stored_member_contacts import (
    import_chamber_stored_member_contacts,
)
from apps.historical_data.services.stored_members import (
    import_chamber_stored_members,
)
# from apps.historical_data.services.team import import_chamber_teams
from apps.historical_data.services.user_campaigns import (
    import_chamber_user_campaigns,
)
from apps.historical_data.services.users import import_chamber_users
from apps.members.models import Contract


# pylint: disable=too-many-locals
def import_all_chamber_data(
    old_chamber_ids: Iterable[int],
    target_chamber_id: int,
) -> dict[str, int]:
    """Call all import services for chamber import."""
    cursor = connection.cursor()
    target_chamber = Chamber.objects.get(id=target_chamber_id)
    campaign_ids = import_chambers(cursor, target_chamber, old_chamber_ids)
    user_ids = import_chamber_users(cursor, campaign_ids, target_chamber)
    # team_ids = import_chamber_teams(cursor, target_chamber)
    user_campaign_ids = import_chamber_user_campaigns(
        cursor,
        campaign_ids,
        target_chamber,
    )
    product_category_ids = import_chamber_inventory(
        cursor,
        target_chamber,
    )
    incentive_ids = import_chamber_incentives(
        cursor,
        campaign_ids,
        target_chamber,
    )
    reward_ids = import_chamber_rewards(cursor, campaign_ids, target_chamber)
    resource_ids = import_chamber_resources(cursor, target_chamber)
    stored_member_ids = import_chamber_stored_members(
        cursor,
        campaign_ids,
        target_chamber,
    )
    stored_member_contact_ids = import_chamber_stored_member_contacts(
        cursor,
        campaign_ids,
        target_chamber,
    )
    contract_ids = import_contracts(cursor, campaign_ids, target_chamber)
    cursor.close()
    return {
        "chambers": len(campaign_ids),
        "users": len(user_ids),
        "campaigns": len(campaign_ids),
        "user_campaigns": len(user_campaign_ids),
        # "teams": len(team_ids),
        "product_categories": len(product_category_ids),
        "products": len(product_category_ids),
        "levels": len(product_category_ids),
        "incentives": len(incentive_ids),
        "rewards": len(reward_ids),
        "resources": len(resource_ids),
        "stored_members": len(stored_member_ids),
        "stored_member_contacts": len(stored_member_contact_ids),
        "contracts": len(contract_ids),
    }


def import_partial(
    target_chamber_id: int,
):
    """Import partial data for chamber import."""
    cursor = connection.cursor()
    target_chamber = Chamber.objects.get(id=target_chamber_id)
    campaign_ids = Campaign.objects.filter(
        chamber=target_chamber,
    ).values_list("external_id", flat=True)
    StoredMember.objects.filter(chamber=target_chamber).delete(force_policy=0)
    stored_member_ids = import_chamber_stored_members(
        cursor,
        campaign_ids,
        target_chamber,
    )
    stored_member_contact_ids = import_chamber_stored_member_contacts(
        cursor,
        campaign_ids,
        target_chamber,
    )
    Contract.objects.filter(
        campaign__chamber=target_chamber,
    ).delete(force_policy=0)
    contract_ids = import_contracts(cursor, campaign_ids, target_chamber)
    return {
        "stored_members": len(stored_member_ids),
        "stored_member_contacts": len(stored_member_contact_ids),
        "contracts": len(contract_ids),
    }
