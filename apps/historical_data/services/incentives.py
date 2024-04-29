from typing import Iterable

from django.db.backends.mysql.base import CursorWrapper

from apps.campaigns.models import Campaign
from apps.chambers.models import Chamber
from apps.historical_data.services import IncentiveData
from apps.incentives.models import Incentive

INCENTIVE_FETCH_SQL_TEMPLATE = """
SELECT
    rewards.id,
    description,
    minimum,
    value,
    sale_types.name,
    chamber
FROM rewards
JOIN sale_types
ON rewards.type = sale_types.id
WHERE chamber in ({list_of_ids})
"""


def fetch_incentive_data(
    cursor: CursorWrapper,
    old_campaign_ids: Iterable[int],
) -> list[IncentiveData]:
    """Select incentives from old db."""
    query = INCENTIVE_FETCH_SQL_TEMPLATE.format(
        list_of_ids=", ".join(["%s" for _ in old_campaign_ids]),
    )
    cursor.execute(query, tuple(old_campaign_ids))
    raw_incentives = cursor.fetchall()
    incentives: list[IncentiveData] = [
        IncentiveData(
            id=incentive[0],
            name=incentive[1],
            threshold=incentive[2],
            value=incentive[3],
            type=incentive[4],
            chamber=incentive[5],
        ) for incentive in raw_incentives
    ]
    return incentives


def import_chamber_incentives(
    cursor: CursorWrapper,
    old_campaign_ids: Iterable[int],
    target_chamber: Chamber,
) -> list[int]:
    """Import old chamber incentives."""
    old_incentives: list[IncentiveData] = fetch_incentive_data(
        cursor=cursor,
        old_campaign_ids=old_campaign_ids,
    )
    new_incentives = []
    old_campaigns = Campaign.objects.filter(
        chamber_id=target_chamber.id,
        external_id__isnull=False,
    ).values_list("external_id", "id")
    chamber_campaign_ids_map: dict[int, int] = dict(old_campaigns)
    for incentive in old_incentives:
        campaign_id = chamber_campaign_ids_map.get(incentive.chamber)
        if not campaign_id:
            continue
        new_incentives.extend(
            [
                Incentive(
                    name=incentive.name,
                    threshold=incentive.threshold,
                    value=incentive.value,
                    type=incentive.type,
                    campaign_id=campaign_id,
                    external_id=incentive.id,
                ),
            ],
        )
    Incentive.objects.bulk_create(new_incentives)
    return [incentive.id for incentive in new_incentives]
