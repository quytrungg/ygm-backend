from typing import Iterable

from django.db.backends.mysql.base import CursorWrapper

from apps.chambers.models import Chamber, StoredMember
from apps.historical_data.services import StoredMemberData

STORED_MEMBER_FETCH_SQL_TEMPLATE = """
SELECT
    companies.id,
    companies.name,
    companies.chamber,
    companies.addr1,
    companies.addr2,
    companies.city,
    companies.state,
    companies.zip,
    companies.fax
FROM companies
WHERE
    companies.chamber in ({list_of_ids}) and (
    companies.addr1 is not null or
    companies.name is not null or
    companies.fax is not null)
GROUP BY
    companies.name,
    companies.addr1,
    companies.fax
"""


def fetch_stored_member_data(
    cursor: CursorWrapper,
    old_chamber_ids: Iterable[int],
) -> list[StoredMemberData]:
    """Select stored members from old db."""
    query = STORED_MEMBER_FETCH_SQL_TEMPLATE.format(
        list_of_ids=", ".join(["%s" for _ in old_chamber_ids]),
    )
    cursor.execute(query, tuple(old_chamber_ids))
    raw_stored_members = cursor.fetchall()
    stored_members: list[StoredMemberData] = [
        StoredMemberData(
            id=member[0],
            name=member[1],
            chamber=member[2],
            address=member[3],
            address2=member[4],
            city=member[5],
            state=member[6],
            zip=member[7],
            phone=member[8],
        ) for member in raw_stored_members
    ]
    return stored_members


def import_chamber_stored_members(
    cursor: CursorWrapper,
    old_chamber_ids: Iterable[int],
    target_chamber: Chamber,
) -> Iterable[int]:
    """Import old chamber stored members."""
    old_stored_members: list[StoredMemberData] = fetch_stored_member_data(
        cursor=cursor,
        old_chamber_ids=old_chamber_ids,
    )
    stored_members = [
        StoredMember(
            name=member.name or "",
            chamber_id=target_chamber.id,
            address=member.address or "",
            address2=member.address2 or "",
            city=member.city or "",
            state=member.state or "",
            zip=member.zip or "",
            phone=member.phone or "",
            external_id=member.id,
        )
        for member in old_stored_members
    ]
    StoredMember.objects.bulk_create(stored_members)
    return [member.id for member in stored_members]
