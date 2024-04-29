from typing import Iterable

from django.db.backends.mysql.base import CursorWrapper

from apps.campaigns.constants import UserCampaignRole
from apps.campaigns.models import Campaign, Team, UserCampaign
from apps.chambers.models import Chamber
from apps.historical_data.services import UserCampaignRelatedInformationData
from apps.users.models import User

USER_CAMPAIGN_RELATED_INFORMATION_FETCH_SQL_TEMPLATE = """
    SELECT
        id,
        name,
        team,
        chamber,
        captain,
        vice_chair
    FROM users
    WHERE chamber in ({list_of_ids})
"""


def fetch_user_campaign_related_information(
    cursor: CursorWrapper,
    old_campaign_ids: Iterable[int],
) -> list[UserCampaignRelatedInformationData]:
    """Get campaign-related information of users."""
    query = USER_CAMPAIGN_RELATED_INFORMATION_FETCH_SQL_TEMPLATE.format(
        list_of_ids=", ".join(["%s" for _ in old_campaign_ids]),
    )
    cursor.execute(query, tuple(old_campaign_ids))
    raw_information = cursor.fetchall()
    user_information = [
        UserCampaignRelatedInformationData(
            id=information[0],
            name=information[1],
            team=information[2],
            chamber=information[3],
            captain=information[4],
            vice_chair=information[5],
        ) for information in raw_information
    ]
    return user_information


def import_chamber_user_campaigns(
    cursor: CursorWrapper,
    old_campaign_ids: Iterable[int],
    target_chamber: Chamber,
) -> list[int]:
    """Import user campaign related information."""
    user_campaign_related_information = (
        fetch_user_campaign_related_information(
            cursor,
            old_campaign_ids,
        )
    )
    user_campaign_related_information_dict = {
        data.id: data
        for data in user_campaign_related_information
    }
    user_campaign_related_information.sort(key=lambda x: x.id)
    user_campaigns: list[UserCampaign] = []
    for user in User.objects.filter(chamber_id=target_chamber.id):
        for campaign in Campaign.objects.filter(chamber_id=target_chamber.id):
            if user.chamber_id != campaign.chamber_id:
                continue
            user_campaign_related_information_data = (
                user_campaign_related_information_dict.get(
                    user.external_id,
                )
            )
            if not user_campaign_related_information_data:
                role = UserCampaignRole.VOLUNTEER
            elif user_campaign_related_information_data.vice_chair:
                role = UserCampaignRole.VICE_CHAIR
            elif user_campaign_related_information_data.captain:
                role = UserCampaignRole.TEAM_CAPTAIN
            else:
                role = UserCampaignRole.VOLUNTEER
            team = None
            if user_campaign_related_information_data:
                team = Team.objects.filter(
                    campaign=campaign,
                    external_id=user_campaign_related_information_data.team,
                ).first()
            user_campaign = UserCampaign(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                user_id=user.id,
                campaign_id=campaign.id,
                team=team,
                role=role,
                external_user_id=user.external_id,
                external_campaign_id=campaign.external_id,
                external_team_id=user_campaign_related_information_data.team if user_campaign_related_information_data else None,  # noqa: E501  pylint: disable=line-too-long
            )
            if team and role != UserCampaignRole.VOLUNTEER:
                user_campaign.save()
                team.managed_by = user_campaign
                team.save()
            else:
                user_campaigns.append(user_campaign)
    user_campaigns = UserCampaign.objects.bulk_create(
        user_campaigns,
        ignore_conflicts=True,
    )
    return [user_campaign.id for user_campaign in user_campaigns]
