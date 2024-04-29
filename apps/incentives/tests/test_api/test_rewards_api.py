from django.urls import reverse_lazy
from django.utils import timezone

from rest_framework import status

import pytest

from apps.campaigns.constants import CampaignStatus, UserCampaignRole
from apps.campaigns.factories import CampaignFactory, UserCampaignFactory
from apps.campaigns.models import Campaign, UserCampaign
from apps.core.test_utils import CAAPIClient
from apps.incentives.factories import IncentiveFactory
from apps.incentives.factories.reward import RewardFactory
from apps.incentives.models import Incentive, Reward
from apps.users.models import User


@pytest.fixture
def campaign(chamber) -> Campaign:
    """Return an open campaign within the chamber."""
    return CampaignFactory(chamber=chamber, status=CampaignStatus.CREATED)


@pytest.fixture
def incentive(campaign) -> Incentive:
    """Return an incentive."""
    return IncentiveFactory(
        campaign=campaign,
        value=100,
    )


@pytest.fixture
def volunteers(campaign) -> list[UserCampaign]:
    """Return a list of volunteers."""
    return [
        UserCampaignFactory(
            campaign=campaign,
            role=UserCampaignRole.VOLUNTEER,
        ) for _ in range(3)
    ]


@pytest.fixture
def rewards(incentive, volunteers) -> list[Reward]:
    """Return a list of rewards for a campaign."""
    return (
        [
            RewardFactory(
                incentive=incentive,
                user_campaign=volunteer,
            ) for volunteer in volunteers
        ] +
        [
            RewardFactory(
                incentive=incentive,
                user_campaign=volunteer,
                paid_at=None,
            ) for volunteer in volunteers
        ]
    )


def test_paid_and_owed_reward_list_api(
    chamber_admin: User,
    campaign: Campaign,
    rewards: list[Reward],
) -> None:
    """Test paid and owed api."""
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(user=chamber_admin)
    url = reverse_lazy("v1:chamber:paid-and-owed-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_incentive_metrics_api(
    chamber_admin: User,
    campaign: campaign,
    incentive: list[Incentive],
) -> None:
    """Ensure CA can access incentive metrics API."""
    user_campaign = UserCampaignFactory(
        campaign=campaign,
        role=UserCampaignRole.VOLUNTEER,
    )
    owed_reward = RewardFactory(
        incentive_id=incentive.id,
        user_campaign_id=user_campaign.id,
    )
    paid_rewards = RewardFactory.create_batch(
        size=3,
        incentive_id=incentive.id,
        user_campaign_id=user_campaign.id,
        paid_at=timezone.now(),
    )
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(chamber_admin)
    response = api_client.get(reverse_lazy("v1:chamber:reward-get-stats"))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_incentives"] == sum(
        reward.incentive.value for reward in paid_rewards
    ) + owed_reward.incentive.value
