from django.urls import reverse_lazy

from rest_framework import status, test

import pytest

from apps.core.test_utils import TestLevelData
from apps.users.models import User

from ...factories import ProductCategoryFactory, ProductFactory
from ...models import Campaign


@pytest.mark.skip(reason="Skip due to new logic")
def test_get_remaining_sponsorship_vs_api(
    active_campaign: Campaign,
    volunteer: User,
    api_client: test.APIClient,
    setup_product,
) -> None:
    """Ensure volunteer can view remaining sponsorship."""
    category = ProductCategoryFactory(campaign=active_campaign)
    product = ProductFactory(category=category)
    test_level_data_list = [
        TestLevelData(
            level_info={"cost": 100},
            total_count=10,
            sold_count=4,
            declined_count=1,
        ),
        TestLevelData(
            level_info={"cost": 500},
            total_count=100,
            sold_count=20,
            declined_count=2,
        ),
    ]
    setup_product(product, test_level_data_list)
    api_client.force_authenticate(volunteer)
    response = api_client.get(
        reverse_lazy("v1:volunteer:remaining-sponsorship-list"),
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.data["results"]
    assert len(data) == len(test_level_data_list)
    for response_data, test_data in zip(data, test_level_data_list):
        assert response_data["sold_instances_count"] == test_data.sold_count
        assert (
            response_data["remaining_instances_count"]
            == test_data.total_count - test_data.sold_count
        )
