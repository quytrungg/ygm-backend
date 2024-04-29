from functools import partial

from django.urls import reverse_lazy

from rest_framework import status

import pytest

from apps.campaigns.models import Campaign, Team
from apps.core.test_utils import CAAPIClient


def get_team_url(action: str, kwargs=None):
    """Return url of team api."""
    return reverse_lazy(f"v1:chamber:team-{action}", kwargs=kwargs)


get_list_team_url = partial(get_team_url, action="list")()
get_detail_team_url = partial(get_team_url, action="detail")
get_team_options_url = partial(get_team_url, action="options")()


@pytest.fixture
def team_create_data() -> dict:
    """Return data to create a team in campaign."""
    return {
        "name": "Test Team",
        "goal": 10000,
    }


@pytest.fixture
def team_update_data(team_create_data: dict) -> dict:
    """Return udpated data of team."""
    return {
        "name": "Updated Team",
        "goal": 20000,
    }


def test_team_list_api(
    chamber_admin_client: CAAPIClient,
    teams: list[Team],
) -> None:
    """Ensure users can view all teams in all campaigns in their chamber."""
    chamber_admin_client.select_campaign(teams[0].campaign)
    response = chamber_admin_client.get(get_list_team_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == len(teams)


def test_team_list_api_fail(
    another_chamber_admin_client: CAAPIClient,
    teams: list[Team],
) -> None:
    """Ensure users from other chambers cannot access the list team api."""
    another_chamber_admin_client.select_campaign(teams[0].campaign)
    response = another_chamber_admin_client.get(get_list_team_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) != len(teams)


def test_team_detail_api(
    chamber_admin_client: CAAPIClient,
    team: Team,
) -> None:
    """Ensure users can view team detail in a campaign of their chamber."""
    chamber_admin_client.select_campaign(team.campaign)
    response = chamber_admin_client.get(
        get_detail_team_url(kwargs={"pk": team.pk}),
    )
    assert response.status_code == status.HTTP_200_OK


def test_team_detail_api_fail(
    another_chamber_admin_client: CAAPIClient,
    team: Team,
) -> None:
    """Ensure users from other chambers can't view team from this chamber."""
    another_chamber_admin_client.select_campaign(team.campaign)
    response = another_chamber_admin_client.get(
        get_detail_team_url(kwargs={"pk": team.pk}),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_team_create_api(
    chamber_admin_client: CAAPIClient,
    team_create_data: dict,
    open_campaign: Campaign,
) -> None:
    """Ensure CA can create a team with given data."""
    chamber_admin_client.select_campaign(open_campaign)
    response = chamber_admin_client.post(
        get_list_team_url,
        data=team_create_data,
    )
    return response.status_code == status.HTTP_201_CREATED


def test_team_update_api(
    chamber_admin_client: CAAPIClient,
    team: Team,
    team_update_data: dict,
) -> None:
    """Ensure CA can update an existing team in campaign of his chamber."""
    chamber_admin_client.select_campaign(team.campaign)
    response = chamber_admin_client.put(
        get_detail_team_url(kwargs={"pk": team.pk}),
        data=team_update_data,
    )
    return response.status_code == status.HTTP_200_OK


def test_team_delete_api(
    chamber_admin_client: CAAPIClient,
    team: Team,
) -> None:
    """Ensure CA can delete a team in campaign of his chamber."""
    chamber_admin_client.select_campaign(team.campaign)
    response = chamber_admin_client.delete(
        get_detail_team_url(kwargs={"pk": team.pk}),
    )
    return response.status_code == status.HTTP_204_NO_CONTENT


def test_team_options_api(
    chamber_admin_client: CAAPIClient,
    teams: list[Team],
) -> None:
    """Ensure team options api return appropriate teams."""
    chamber_admin_client.select_campaign(teams[0].campaign)
    response = chamber_admin_client.get(get_team_options_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == len(teams)
