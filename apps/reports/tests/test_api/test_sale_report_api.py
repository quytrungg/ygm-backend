from django.urls import reverse_lazy

from rest_framework.test import APIClient

import pytest

from apps.campaigns import factories as campaigns_factories
from apps.campaigns import models as campaigns_models
from apps.campaigns.constants import DEFAULT_PRODUCT_CATEGORIES
from apps.chambers import models as chambers_models
from apps.core.test_utils import TestLevelData
from apps.users import factories as users_factories
from apps.users import models as users_models


@pytest.fixture
def open_campaign(
    chamber: chambers_models.Chamber,
) -> campaigns_models.Campaign:
    """Return an open campaign."""
    return campaigns_factories.CampaignFactory(
        chamber=chamber,
        status=campaigns_models.Campaign.STATUSES.CREATED,
    )


@pytest.fixture
def chamber_admin(chamber: chambers_models.Chamber) -> users_models.User:
    """Return a chamber admin."""
    return users_factories.UserFactory(
        chamber=chamber,
        role=users_models.User.ROLES.CHAMBER_ADMIN,
    )


def get_sale_report_url(action_name: str, kwargs: dict | None = None):
    """Return url for sale report APIs."""
    return reverse_lazy(
        f"v1:chamber:sale-{action_name}",
        kwargs=kwargs,
    )


sale_report_list_url = get_sale_report_url(action_name="list")
sale_report_statistics_url = get_sale_report_url(action_name="statistics")


@pytest.fixture
def campaign_inventory(
    open_campaign: campaigns_models.Campaign,
    setup_product,
) -> list[campaigns_models.ProductCategory]:
    """Set up campaign's inventory to test sale report APIs."""
    category_1 = campaigns_factories.ProductCategoryFactory(
        campaign=open_campaign,
    )
    category_1_product_1 = campaigns_factories.ProductFactory(
        category=category_1,
    )
    setup_product(
        category_1_product_1,
        [
            TestLevelData(
                level_info={"cost": 100},
                total_count=2,
                sold_count=0,
                declined_count=1,
            ),
            TestLevelData(
                level_info={"cost": 200},
                total_count=5,
                sold_count=1,
                declined_count=2,
            ),
        ],
    )
    category_2 = campaigns_factories.ProductCategoryFactory(
        campaign=open_campaign,
    )
    category_2_product_1 = campaigns_factories.ProductFactory(
        category=category_2,
    )
    setup_product(
        category_2_product_1,
        [
            TestLevelData(
                level_info={"cost": 300}, total_count=2, sold_count=1,
            ),
            TestLevelData(
                level_info={"cost": 150}, total_count=2, sold_count=1,
            ),
        ],
    )
    category_2_product_2 = campaigns_factories.ProductFactory(
        category=category_2,
    )
    setup_product(
        category_2_product_2,
        [
            TestLevelData(
                level_info={"cost": 5000},
                total_count=1,
                sold_count=1,
                declined_count=1,
            ),
        ],
    )
    return [category_1, category_2]


@pytest.mark.skip(reason="Skip due to new logic")
def test_sale_statistics_api(
    campaign_inventory,
    chamber_admin: users_models.User,
):
    """Ensure statistics are calculated correctly."""
    client = APIClient()
    client.force_login(chamber_admin)
    response = client.get(sale_report_statistics_url)
    assert response.status_code == 200, response.data
    assert response.data["total_sold_value"] == 5650
    assert response.data["total_available_value"] == 1450
    assert response.data["total_sold_count"] == 4
    assert response.data["total_available_count"] == 8


@pytest.mark.skip(reason="Skip due to new logic")
def test_product_category_sale_report_api(
    campaign_inventory: list[campaigns_models.ProductCategory],
    chamber_admin: users_models.User,
):
    """Ensure product categories ."""
    client = APIClient()
    client.force_login(chamber_admin)
    response = client.get(sale_report_list_url)
    assert response.status_code == 200, response.data
    results = response.data["results"]
    assert len(results) == (
        len(campaign_inventory) + len(DEFAULT_PRODUCT_CATEGORIES)
    )
    assert sum(category["sold_value"] for category in results) == 5650
    assert sum(category["remaining_value"] for category in results) == 1450
