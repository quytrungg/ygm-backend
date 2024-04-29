from functools import partial
from operator import attrgetter, itemgetter

from django.urls import reverse_lazy

from rest_framework import status, test

import pytest

from apps.core.test_utils import TestLevelData

from ...factories import ProductCategoryFactory, ProductFactory
from ...models import Campaign


def get_product_url(action_name: str, kwargs=None):
    """Return url for product's public APIs."""
    return reverse_lazy(
        f"v1:public:product-{action_name}",
        kwargs=kwargs,
    )


get_list_product_url = partial(get_product_url, action_name="list")


@pytest.mark.parametrize(
    argnames="campaign",
    argvalues=[
        pytest.lazy_fixture("open_campaign"),
        pytest.lazy_fixture("active_campaign"),
        pytest.lazy_fixture("completed_campaign"),
    ],
)
def test_get_list_product_public(
    setup_product,
    campaign: Campaign,
):
    """Ensure API returns correct data."""
    category = ProductCategoryFactory(campaign=campaign)
    product_1 = ProductFactory(category=category)
    setup_product(
        product_1,
        [
            TestLevelData(
                level_info={"cost": 100},
                total_count=2,
                sold_count=1,
            ),
            TestLevelData(
                level_info={"cost": 100},
                total_count=3,
                sold_count=2,
            ),
        ],
    )
    product_2 = ProductFactory(category=category)
    setup_product(
        product_2,
        [
            TestLevelData(
                level_info={"cost": 100},
                total_count=10,
                sold_count=3,
            ),
            TestLevelData(
                level_info={"cost": 100},
                total_count=10,
                sold_count=4,
            ),
        ],
    )
    api_client = test.APIClient()
    response = api_client.get(
        get_list_product_url(),
        data={
            "category": category.pk,
            "chamber": category.campaign.chamber_id,
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.data

    products = [product_1, product_2]
    assert response.data["count"] == len(products)
    products_data: list[dict] = response.data["results"]
    assert (
        set(item["id"] for item in products_data)
        == set(product.id for product in products)
    )
    products.sort(key=attrgetter("id"))
    products_data.sort(key=itemgetter("id"))
    for product_data, product in zip(products_data, products):
        assert len(product_data["levels"]) == product.levels.count()
