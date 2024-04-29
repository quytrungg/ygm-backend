from typing import Iterable

from django.db.backends.mysql.base import CursorWrapper

from apps.chambers.models import Chamber
from apps.historical_data.services import ResourceData
from apps.resources.models import Resource, ResourceCategory

RESOURCE_FETCH_SQL = """
SELECT
    id,
    file_name,
    file_path,
    file_type,
    object_id
FROM medias
"""


def fetch_resource_data(
    cursor: CursorWrapper,
) -> list[ResourceData]:
    """Select resources from old db."""
    cursor.execute(RESOURCE_FETCH_SQL)
    raw_resources = cursor.fetchall()
    resources: list[ResourceData] = [
        ResourceData(
            id=resource[0],
            name=resource[1],
            file=resource[2],
            file_type=resource[3],
            campaign_id=resource[4],
        ) for resource in raw_resources
    ]
    return resources


def import_chamber_resources(
    cursor: CursorWrapper,
    target_chamber: Chamber,
) -> Iterable[int]:
    """Import old chamber resources."""
    old_resources: list[ResourceData] = fetch_resource_data(
        cursor=cursor,
    )
    default_resource_category, _ = ResourceCategory.objects.get_or_create(
        name="Trainings",
        chamber_id=target_chamber.id,
    )
    new_resources = []
    for resource in old_resources:
        new_resources.append(
            Resource(
                name=resource.name,
                file=resource.file,
                file_type=resource.file_type,
                category_id=default_resource_category.id,
                external_id=resource.id,
                user_group=[],
            ),
        )
    Resource.objects.bulk_create(new_resources)
    return [resource.id for resource in new_resources]
