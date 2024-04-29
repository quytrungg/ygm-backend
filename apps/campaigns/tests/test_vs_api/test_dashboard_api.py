from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.test import APIClient

import pytest

from apps.campaigns.factories import LevelInstanceFactory, UserCampaignFactory
from apps.campaigns.models import Campaign, LevelInstance, UserCampaign
from apps.incentives.factories import IncentiveFactory
from apps.incentives.models import Incentive
from apps.members.factories import ContractFactory
from apps.members.models import Contract, ContractCreditInfo
from apps.users.models import User


@pytest.fixture
def campaign_user(active_campaign: Campaign, volunteer: User) -> UserCampaign:
    """Return a campaign user."""
    return UserCampaignFactory(user=volunteer, campaign=active_campaign)


@pytest.fixture
def approved_contract(
    active_campaign: Campaign,
    campaign_user: User,
) -> Contract:
    """Return an approved contract instance."""
    _contract = ContractFactory(
        status=Contract.STATUSES.APPROVED,
        campaign=active_campaign,
        created_by=campaign_user,
    )
    ContractCreditInfo.objects.create(
        user_campaign=campaign_user,
        contract=_contract,
        portion=1,
    )
    return _contract


@pytest.fixture
def sold_levels(approved_contract: Contract) -> list[LevelInstance]:
    """Return level instances attached to approved contracts."""
    return LevelInstanceFactory.create_batch(
        size=5,
        contract=approved_contract,
    )


@pytest.fixture
def next_incentive(
    active_campaign: Campaign,
    sold_levels: list[LevelInstance],
) -> Incentive:
    """Return next incentive level for campaign user."""
    sold_revenue = sum(level.cost for level in sold_levels)
    return IncentiveFactory(
        threshold=sold_revenue * 2,
        campaign_id=active_campaign.id,
    )


@pytest.fixture
def trip_incentive(
    active_campaign: Campaign,
    next_incentive: Incentive,
) -> Incentive:
    """Return trip incentive for campaign user."""
    return IncentiveFactory(
        threshold=next_incentive.threshold * 2,
        type=Incentive.TYPES.TRIP,
        campaign_id=active_campaign.id,
    )


# pylint: disable=too-many-arguments
def test_campaign_vs_dashboard_statistics_api(
    volunteer: User,
    api_client: APIClient,
    sold_levels: list[LevelInstance],
    active_campaign: Campaign,
    campaign_user: UserCampaign,
    next_incentive: Incentive,
    trip_incentive: Incentive,
) -> None:
    """Ensure volunteers can access campaign dashboard."""
    other_approved_contract = ContractFactory(
        status=Contract.STATUSES.APPROVED,
        campaign=active_campaign,
    )
    other_sold_levels = LevelInstanceFactory.create_batch(
        size=5,
        contract=other_approved_contract,
    )
    api_client.force_authenticate(volunteer)
    response = api_client.get(
        reverse_lazy("v1:volunteer:dashboard-get-stats"),
    )

    assert response.status_code == status.HTTP_200_OK, response.data
    dashboard_data = response.data
    assert dashboard_data["campaign_goal"] == active_campaign.goal
    assert dashboard_data["campaign_total"] == (
        sum(level.cost for level in sold_levels)
        + sum(level.cost for level in other_sold_levels)
    )
    assert dashboard_data["total_raised"] == sum(
        level.cost for level in sold_levels
    )
    assert dashboard_data["personal_goal"] == campaign_user.sales_goal
    assert dashboard_data["remaining_to_next_incentive"] == (
        next_incentive.threshold - dashboard_data["total_raised"]
    )


def test_campaign_vs_dashboard_recently_sold_api(
    volunteer: User,
    api_client: APIClient,
    sold_levels: list[LevelInstance],
    active_campaign: Campaign,
    campaign_user: UserCampaign,
) -> None:
    """Ensure recently sold list API returns appropriate data."""
    api_client.force_authenticate(volunteer)
    response = api_client.get(reverse_lazy("v1:volunteer:recently-sold-list"))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == len(sold_levels)
