import datetime
from collections import OrderedDict
from decimal import Decimal

from django.urls import reverse_lazy
from django.utils import timezone

from rest_framework import status

import pytest

from apps.chambers.factories import ChamberFactory
from apps.core.test_utils import TestLevelData
from apps.users.factories import UserFactory
from apps.users.models import User

from ... import factories as campaign_factories
from ...constants import UserCampaignRole
from ...models import Campaign, UserCampaign


@pytest.fixture
def leaderboard_test_data(setup_product, django_db_blocker):
    """Return data setup for leaderboard APIs tests."""
    with django_db_blocker.unblock():
        chamber = ChamberFactory()
        UserFactory(role=User.ROLES.CHAMBER_CHAIR, chamber=chamber)
        campaign = campaign_factories.CampaignFactory(
            chamber=chamber,
            status=Campaign.STATUSES.LIVE,
            has_vice_chairs=True,
        )
        vice_chair_1 = campaign_factories.UserCampaignFactory(
            campaign=campaign,
            role=UserCampaignRole.VICE_CHAIR,
        )
        vice_chair_2 = campaign_factories.UserCampaignFactory(
            campaign=campaign,
            role=UserCampaignRole.VICE_CHAIR,
        )
        team_1 = campaign_factories.TeamFactory(
            campaign=campaign,
            managed_by=vice_chair_1,
        )
        team_2 = campaign_factories.TeamFactory(
            campaign=campaign,
            managed_by=vice_chair_2,
        )
        product_category = campaign_factories.ProductCategoryFactory(
            campaign=campaign,
        )
        product_1 = campaign_factories.ProductFactory(
            category=product_category,
        )
        product_1_levels = setup_product(
            product_1,
            [
                TestLevelData(
                    level_info={"cost": 100},
                    total_count=10,
                    sold_count=4,
                    declined_count=1,
                ),
                TestLevelData(
                    level_info={"cost": 100},
                    total_count=10,
                    sold_count=4,
                    declined_count=1,
                ),
            ],
        )
        UserCampaign.objects.filter(
            created_contracts__levels__level_id__in=[
                level.id for level in product_1_levels
            ],
        ).update(team=team_1)
        product_2 = campaign_factories.ProductFactory(
            category=product_category,
        )
        product_2_levels = setup_product(
            product_2,
            [
                TestLevelData(
                    level_info={"cost": 200},
                    sold_count=1,
                    total_count=2,
                ),
            ],
        )
        UserCampaign.objects.filter(
            created_contracts__levels__level_id__in=[
                level.id for level in product_2_levels
            ],
        ).update(team=team_2)
        yield {
            "chamber": chamber,
            "campaign": campaign,
            "vice_chair_1": vice_chair_1,
            "vice_chair_2": vice_chair_2,
            "team_1": team_1,
            "team_2": team_2,
            "product_1_levels": product_1_levels,
            "product_2_levels": product_2_levels,
        }
        chamber.hard_delete()


def test_get_team_standings_api(leaderboard_test_data, api_client):
    """Ensure API returns correct data."""
    volunteer = User.objects.filter(
        role=User.ROLES.VOLUNTEER,
        chamber=leaderboard_test_data["chamber"],
    ).first()
    api_client.force_authenticate(volunteer)
    response = api_client.get(
        reverse_lazy("v1:volunteer:team-standing-list"),
        data={
            "revenue_from": timezone.now() - datetime.timedelta(days=3),
            "revenue_to": timezone.now() + datetime.timedelta(days=4),
            "ordering": "-total_revenue",
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.data
    data = response.data["results"]
    vice_chair_1 = leaderboard_test_data["vice_chair_1"]
    team_1 = leaderboard_test_data["team_1"]
    vice_chair_2 = leaderboard_test_data["vice_chair_2"]
    team_2 = leaderboard_test_data["team_2"]

    assert data == [
        OrderedDict(
            {
                "id": vice_chair_1.id,
                "first_name": vice_chair_1.first_name,
                "last_name": vice_chair_1.last_name,
                "role": "vice_chair",
                "managed_teams": [
                    OrderedDict(
                        {
                            "id": team_1.id,
                            "name": team_1.name,
                            "goal": team_1.goal,
                            "week_revenue": Decimal(800),
                            "total_revenue": Decimal(800),
                            "total_cash_revenue": Decimal(800),
                        },
                    ),
                ],
            },
        ),
        OrderedDict(
            {
                "id": vice_chair_2.id,
                "first_name": vice_chair_2.first_name,
                "last_name": vice_chair_2.last_name,
                "role": "vice_chair",
                "managed_teams": [
                    OrderedDict(
                        {
                            "id": team_2.id,
                            "name": team_2.name,
                            "goal": team_2.goal,
                            "week_revenue": Decimal(200),
                            "total_revenue": Decimal(200),
                            "total_cash_revenue": Decimal(200),
                        },
                    ),
                ],
            },
        ),
    ]


def test_get_volunteer_standings_api(leaderboard_test_data, api_client):
    """Ensure API returns correct data."""
    volunteer = User.objects.filter(
        role=User.ROLES.VOLUNTEER,
        chamber=leaderboard_test_data["chamber"],
    ).first()
    api_client.force_authenticate(volunteer)
    response = api_client.get(
        reverse_lazy("v1:volunteer:volunteer-standing-list"),
        data={
            "revenue_from": timezone.now() - datetime.timedelta(days=3),
            "revenue_to": timezone.now() + datetime.timedelta(days=4),
            "ordering": "-week_revenue,id",
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.data
    data = response.data["results"]
    assert len(data) == 4


def test_get_leadership_standings_api(leaderboard_test_data, api_client):
    """Ensure API returns correct data."""
    volunteer = User.objects.filter(
        role=User.ROLES.VOLUNTEER,
        chamber=leaderboard_test_data["chamber"],
    ).first()
    api_client.force_authenticate(volunteer)
    response = api_client.get(
        reverse_lazy("v1:volunteer:leadership-standing-list"),
        data={
            "revenue_from": timezone.now() - datetime.timedelta(days=3),
            "revenue_to": timezone.now() + datetime.timedelta(days=4),
            "ordering": "-week_revenue",
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.data
    data = response.data["results"]
    vice_chair_1 = leaderboard_test_data["vice_chair_1"]
    vice_chair_2 = leaderboard_test_data["vice_chair_2"]

    assert data == [
        OrderedDict(
            {
                "id": vice_chair_1.id,
                "first_name": vice_chair_1.first_name,
                "last_name": vice_chair_1.last_name,
                "role": "vice_chair",
                "total_revenue": Decimal(800),
                "week_revenue": Decimal(800),
                "total_cash_revenue": Decimal(800),
            },
        ),
        OrderedDict(
            {
                "id": vice_chair_2.id,
                "first_name": vice_chair_2.first_name,
                "last_name": vice_chair_2.last_name,
                "role": "vice_chair",
                "total_revenue": Decimal(200),
                "week_revenue": Decimal(200),
                "total_cash_revenue": Decimal(200),
            },
        ),
    ]
