import decimal
from typing import Iterable

from django.db.backends.mysql.base import CursorWrapper

from apps.campaigns.models import Campaign, Level, Product, ProductCategory
from apps.chambers.models import Chamber
from apps.historical_data.services import (
    EventData,
    EventTypeData,
    SponsorshipData,
)

SPONSORSHIPS_FETCH_SQL_TEMPLATE = """
    SELECT
        id,
        chamber,
        event,
        name,
        available,
        cost,
        benefits,
        position,
        multiplier
    FROM sponsorships
    WHERE event=%s
"""

EVENTS_FETCH_BY_TYPE_TEMPLATE = """
    SELECT
        id,
        chamber,
        date,
        name,
        description
    FROM events
    where type=%s
"""

EVENTS_FETCH_BY_CAMPAIGN_TEMPLATE = """
    SELECT
        id,
        chamber,
        date,
        name,
        description
    FROM events
    where chamber=%s and type is null
"""

EVENT_TYPES_FETCH_TEMPLATE = """
    SELECT
        id,
        chamber,
        name
    FROM event_types
    WHERE chamber in ({list_of_ids})
"""


def fetch_event_types(
    cursor: CursorWrapper,
    old_campaign_ids,
) -> Iterable[EventTypeData]:
    """Fetch events."""
    query = EVENT_TYPES_FETCH_TEMPLATE.format(
        list_of_ids=", ".join(["%s" for _ in old_campaign_ids]),
    )
    cursor.execute(query, tuple(old_campaign_ids))
    event_types: list[EventTypeData] = []
    for row in cursor.fetchall():
        event_type = EventTypeData(
            id=row[0],
            chamber=row[1],
            name=row[2],
        )
        event_types.append(event_type)
    return event_types


def fetch_events_by_campaign(
    cursor: CursorWrapper,
    old_campaign_id,
):
    """Fetch events by campaign."""
    cursor.execute(
        EVENTS_FETCH_BY_CAMPAIGN_TEMPLATE,
        (old_campaign_id,),
    )
    events: list[EventData] = []
    for row in cursor.fetchall():
        event = EventData(
            id=row[0],
            date=row[2],
            name=row[3],
            description=row[4],
        )
        events.append(event)
    return events


def fetch_events_by_type(
    cursor: CursorWrapper,
    type_id,
):
    """Fetch event by type."""
    cursor.execute(
        EVENTS_FETCH_BY_TYPE_TEMPLATE,
        (type_id,),
    )
    events: list[EventData] = []
    for row in cursor.fetchall():
        event = EventData(
            id=row[0],
            date=row[2],
            name=row[3],
            description=row[4],
        )
        events.append(event)
    return events


def fetch_sponsorships(
    cursor: CursorWrapper,
    event_id: int,
) -> list[SponsorshipData]:
    """Get users from selected chamber."""
    cursor.execute(SPONSORSHIPS_FETCH_SQL_TEMPLATE, (event_id,))
    rows = cursor.fetchall()
    sponsorships: list[SponsorshipData] = [
        SponsorshipData(
            id=sponsorship[0],
            chamber=sponsorship[1],
            event=sponsorship[2],
            name=sponsorship[3],
            available=sponsorship[4],
            cost=sponsorship[5],
            benefits=sponsorship[6] or "",
            position=sponsorship[7],
            multiplier=sponsorship[8],
        ) for sponsorship in rows
    ]
    return sponsorships


def import_chamber_inventory(
    cursor: CursorWrapper,
    target_chamber: Chamber,
) -> list[int]:
    """Import inventory based on exiting Sponsorships."""
    campaigns = Campaign.objects.filter(
        chamber_id=target_chamber.id,
        external_id__isnull=False,
    )
    product_categories = []
    products = []
    for campaign in campaigns:
        old_event_types = fetch_event_types(
            cursor,
            [campaign.external_id],
        )
        product_categories.extend(
            ProductCategory.objects.bulk_create([
                ProductCategory(
                    name=old_event_type.name,
                    campaign=campaign,
                    background_color="#000000",
                    external_id=old_event_type.id,
                ) for old_event_type in old_event_types
            ]),
        )
        default_category = ProductCategory(
            name="Default",
            campaign=campaign,
            background_color="#000000",
        )
        default_category.save()
        events_without_category = fetch_events_by_campaign(
            cursor,
            campaign.external_id,
        )
        products.extend(
            Product.objects.bulk_create(
                [
                    Product(
                        category=default_category,
                        name=event.name,
                        pre_trc_income=decimal.Decimal(0),
                        description=event.description or "",
                        is_included_in_renewal=True,
                        external_id=event.id,
                    ),
                ] for event in events_without_category
            ),
        )

    for product_category in product_categories:
        events = fetch_events_by_type(
            cursor,
            product_category.external_id,
        )
        products.extend(
            Product.objects.bulk_create(
                [
                    Product(
                        category=product_category,
                        name=event.name,
                        pre_trc_income=decimal.Decimal(0),
                        description=event.description or "",
                        is_included_in_renewal=True,
                        external_id=event.id,
                    ) for event in events
                ],
            ),
        )

    for product in products:
        old_sponsorships = fetch_sponsorships(
            cursor,
            product.external_id,
        )
        Level.objects.bulk_create([
            Level(
                product=product,
                name=sponsorship.name,
                cost=sponsorship.cost or 0,
                amount=sponsorship.available or 0,
                benefits=sponsorship.benefits,
                description="",
                conditions="",
                external_id=sponsorship.id,
                external_multiplier=sponsorship.multiplier,
            ) for sponsorship in old_sponsorships
        ])

    return [product_category.id for product_category in product_categories]
