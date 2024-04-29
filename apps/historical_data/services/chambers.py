import operator
from typing import Iterable

from django.core.files.base import ContentFile
from django.db.backends.mysql.base import CursorWrapper

import requests

from apps.campaigns.constants import CampaignStatus
from apps.campaigns.models import Campaign
from apps.chambers.models import Chamber
from apps.historical_data.services import ChamberData

CHAMBER_FETCH_SQL_TEMPLATE = """
    SELECT
        id,
        name,
        description,
        created,
        (select value from chamber_settings where chamber=chambers.id and name='chamber_logo') as logo
    FROM chambers
    WHERE id IN ({list_of_ids})
"""     # noqa: E501


def fetch_chambers(
    cursor: CursorWrapper,
    chamber_ids: Iterable[int],
) -> list[ChamberData]:
    """Select passed chambers from old db."""
    query = CHAMBER_FETCH_SQL_TEMPLATE.format(
        list_of_ids=", ".join(["%s" for _ in chamber_ids]),
    )
    cursor.execute(query, tuple(chamber_ids))
    raw_chambers = cursor.fetchall()
    chambers: list[ChamberData] = [
        ChamberData(
            id=chamber[0],
            nickname=chamber[1],
            subdomain=chamber[1],
            name=chamber[1],
            description=chamber[2],
            created=chamber[3],
            logo=chamber[4],
        ) for chamber in raw_chambers
    ]
    return chambers


def import_chambers(
    cursor: CursorWrapper,
    target_chamber: Chamber,
    old_chamber_ids: Iterable[int] | None = None,
) -> list[int]:
    """Import chambers from with passed old chamber ids."""
    old_chambers = fetch_chambers(cursor, old_chamber_ids)
    campaigns = Campaign.objects.bulk_create([
        Campaign(
            name=old_chamber.name,
            year=old_chamber.year,
            chamber=target_chamber,
            status=CampaignStatus.DONE,
            external_id=old_chamber.id,
        ) for old_chamber in old_chambers
    ])
    if old_chambers:
        newest_chamber = next(
            iter(
                sorted(
                    [chamber for chamber in old_chambers if chamber.logo],
                    key=operator.attrgetter("id"),
                ),
            ),
            None,
        )
        if newest_chamber:
            logo = requests.get(newest_chamber.logo, timeout=10).content
            target_chamber.branding.chamber_logo = ContentFile(logo)
            target_chamber.branding.chamber_logo.save(
                f"logo_{target_chamber.id}",
                ContentFile(logo),
                save=True,
            )
    return [campaign.external_id for campaign in campaigns]
