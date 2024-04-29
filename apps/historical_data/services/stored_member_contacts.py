from typing import Iterable

from django.db.backends.mysql.base import CursorWrapper

from apps.chambers.models import Chamber, StoredMember, StoredMemberContact
from apps.historical_data.services import (
    StoredMemberContactData,
    StoredMemberData,
)

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
    companies.fax,
    contact_infos.id,
    contact_infos.first_name,
    contact_infos.last_name,
    contact_infos.email,
    contact_infos.phone,
    contact_infos.cellphone
FROM companies, contact_infos
WHERE
    contact_infos.company = companies.id and
    companies.chamber in ({list_of_ids}) and (
    companies.addr1 is not null or
    companies.name is not null or
    companies.fax is not null)
GROUP BY
    companies.name,
    companies.addr1,
    contact_infos.first_name,
    contact_infos.last_name,
    contact_infos.email,
    contact_infos.phone,
    contact_infos.cellphone
"""


def fetch_stored_member_contact_data(
    cursor: CursorWrapper,
    old_campaign_ids: Iterable[int],
) -> list[StoredMemberData]:
    """Select stored member contacts from old db."""
    query = STORED_MEMBER_FETCH_SQL_TEMPLATE.format(
        list_of_ids=", ".join(["%s" for _ in old_campaign_ids]),
    )
    cursor.execute(query, tuple(old_campaign_ids))
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
            contact=StoredMemberContactData(
                id=member[9],
                first_name=member[10],
                last_name=member[11],
                email=member[12],
                work_phone=member[13],
                mobile_phone=member[14],
            ),
        ) for member in raw_stored_members
    ]
    return stored_members


def import_chamber_stored_member_contacts(
    cursor: CursorWrapper,
    old_campaign_ids: Iterable[int],
    target_chamber: Chamber,
) -> Iterable[int]:
    """Import old chamber stored member contacts."""
    old_stored_members = fetch_stored_member_contact_data(
        cursor=cursor,
        old_campaign_ids=old_campaign_ids,
    )
    new_stored_member_contacts = []
    stored_members = StoredMember.objects.filter(
        chamber_id=target_chamber.id,
    ).values_list("name", "address", "phone", "id")
    stored_members_map = {
        (
            stored_member[0],
            stored_member[1],
            stored_member[2],
        ): stored_member[3] for stored_member in stored_members
    }
    for old_stored_member in old_stored_members:
        stored_member_id = stored_members_map.get((
            old_stored_member.name,
            old_stored_member.address,
            old_stored_member.phone,
        ))
        if not stored_member_id:
            continue
        contact = old_stored_member.contact
        new_stored_member_contacts.append(
            StoredMemberContact(
                stored_member_id=stored_member_id,
                first_name=contact.first_name or "",
                last_name=contact.last_name or "",
                email=contact.email or "",
                work_phone=contact.work_phone or "",
                mobile_phone=contact.mobile_phone or "",
                external_id=contact.id,
            ),
        )
    StoredMemberContact.objects.bulk_create(new_stored_member_contacts)
    return [contact.id for contact in new_stored_member_contacts]
