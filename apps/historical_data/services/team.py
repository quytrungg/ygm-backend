from django.db.backends.mysql.base import CursorWrapper

from apps.campaigns.models import Campaign, Team
from apps.chambers.models import Chamber
from apps.historical_data.services import TeamData

TEAM_FETCH_SQL_TEMPLATE = """
    SELECT
        id,
        chamber,
        name,
        vice_chair,
        goal
    FROM teams
    WHERE chamber=%s
"""


def fetch_teams(
    cursor: CursorWrapper,
    chamber_id: int,
) -> list[TeamData]:
    """Fetch teams data from old database."""
    cursor.execute(TEAM_FETCH_SQL_TEMPLATE, (chamber_id,))
    raw_teams = cursor.fetchall()
    teams: list[TeamData] = [
        TeamData(
            id=team[0],
            chamber=team[1],
            name=team[2],
            vice_chair=team[3],
            goal=team[4],
        ) for team in raw_teams
    ]
    return teams


def import_chamber_teams(
    cursor: CursorWrapper,
    target_chamber: Chamber,
):
    """Import teams related to the old chamber."""
    campaigns = Campaign.objects.filter(
        chamber_id=target_chamber.id,
        external_id__isnull=False,
    )
    new_teams: list[Team] = []
    for campaign in campaigns:
        old_teams = fetch_teams(cursor, campaign.external_id)
        for old_team in old_teams:
            new_teams.append(
                Team(
                    campaign_id=campaign.id,
                    name=old_team.name or "Default Team Name",
                    goal=old_team.goal or 0,
                    managed_by_id=None,
                    external_id=old_team.id,
                ),
            )
    teams = Team.objects.bulk_create(new_teams)
    return [team.id for team in teams]
