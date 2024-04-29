from django.db.backends.mysql.base import CursorWrapper

from apps.chambers.models import Chamber
from apps.historical_data.services import ChamberUserData
from apps.users.constants import UserRole
from apps.users.models import User

CHAMBER_USERS_FETCH_SQL = """
    SELECT
        users.id,
        users.chamber,
        name,
        first_name,
        last_name,
        addr1,
        addr2,
        email,
        phone,
        company
    FROM users, contact_infos
    WHERE
        users.contact_info = contact_infos.id AND
        users.chamber = %s
"""


def fetch_chamber_users(
    cursor: CursorWrapper,
    campaign_id: int,
) -> list[ChamberUserData]:
    """Get users from selected chamber."""
    cursor.execute(CHAMBER_USERS_FETCH_SQL, (campaign_id,))
    rows = cursor.fetchall()
    chamber_users: list[ChamberUserData] = [
        ChamberUserData(
            id=user[0],
            chamber_id=user[1],
            name=user[2],
            first_name=user[3],
            last_name=user[4],
            address=f"{user[5]} {user[6]}",
            email=user[7],
            phone=user[8],
        ) for user in rows
    ]
    return chamber_users


def import_chamber_users(
    cursor: CursorWrapper,
    old_campaign_ids: list[int],
    target_chamber: Chamber,
) -> list[int]:
    """Import user from old db related to passed chambers."""
    new_users: list[User] = []
    for old_campaign_id in old_campaign_ids:
        old_users: list[ChamberUserData] = fetch_chamber_users(
            cursor,
            old_campaign_id,
        )
        new_users = [
            User(
                chamber=target_chamber,
                external_id=user.id,
                external_chamber_id=user.chamber_id,
                first_name=user.first_name,
                last_name=user.last_name,
                address=user.address,
                email=user.updated_email(
                    target_chamber.subdomain,
                ),
                mobile_phone=user.updated_phone(),
                role=UserRole.VOLUNTEER,
            ) for user in old_users
        ]
        User.objects.bulk_create(
            new_users,
            ignore_conflicts=True,
        )
    return [user.id for user in new_users]
