from django.db.backends.mysql.base import CursorWrapper

from apps.campaigns.constants import CampaignStatus
from apps.campaigns.models import Campaign
from apps.chambers.models import Chamber
from apps.historical_data.services import CampaignData

CAMPAIGN_FETCH_SQL = """
SELECT
    events.id AS id,
    events.chamber AS chamber,
    events.name AS name,
    events.date AS date,
    events.description AS description,
    events.contact AS contact,
    event_types.name AS event_type_name,
    event_types.position AS event_type_position
FROM events
JOIN event_types ON events.type = event_types.id
WHERE events.chamber=%s
UNION SELECT
    events.id AS id,
    events.chamber AS chamber,
    events.name AS name,
    events.date AS date,
    events.description AS description,
    events.contact AS contact,
    NULL AS event_type_name,
    NULL AS event_type_position
FROM events
WHERE events.type IS NULL AND events.chamber=%s;
"""


def fetch_campaign_data(
    cursor: CursorWrapper,
    chamber_id: int,
) -> list[CampaignData]:
    """Select chambers from old db."""
    cursor.execute(CAMPAIGN_FETCH_SQL, (chamber_id, chamber_id))
    raw_campaigns = cursor.fetchall()
    campaigns: list[CampaignData] = [
        CampaignData(
            id=campaign[0],
            chamber=campaign[1],
            _name=campaign[2],
            date=campaign[3],
            description=campaign[4],
            contact=campaign[5],
            _type=campaign[6],
            position=campaign[7],
        ) for campaign in raw_campaigns
    ]
    return campaigns


def import_chamber_campaigns(
    cursor: CursorWrapper,
    old_chamber_ids: list[int],
    target_chamber: Chamber,
) -> list[int]:
    """Import campaigns based on exiting Chambers."""
    new_campaigns: list[Campaign] = []
    for old_chamber_id in old_chamber_ids:
        old_campaigns: list[CampaignData] = fetch_campaign_data(
            cursor,
            old_chamber_id,
        )
        new_campaigns.extend(
            Campaign.objects.bulk_create(
                [
                    Campaign(
                        name=campaign.get_name(target_chamber.name),
                        chamber_id=target_chamber.id,
                        status=CampaignStatus.DONE,
                        year=campaign.year,
                        start_date=campaign.date,
                        external_id=campaign.id,
                        external_type=campaign.get_type(),
                        external_position=campaign.position,
                        external_chamber_id=old_chamber_id,
                    ) for campaign in old_campaigns
                ],
            ),
        )
    return [campaign.id for campaign in new_campaigns]
