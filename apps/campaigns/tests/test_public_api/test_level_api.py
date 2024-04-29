from functools import partial

from django.urls import reverse_lazy

from rest_framework import status, test

import pytest

from apps.core.test_utils import TestLevelData

from ...factories import ProductCategoryFactory, ProductFactory
from ...models import Campaign, Level


def get_level_url(action_name: str, kwargs=None):
    """Return url for level's public APIs."""
    return reverse_lazy(
        f"v1:public:level-{action_name}",
        kwargs=kwargs,
    )


get_detail_level_url = partial(
    get_level_url,
    action_name="detail",
)


@pytest.mark.parametrize(
    argnames=["campaign", "expected_status"],
    argvalues=[
        [pytest.lazy_fixture("open_campaign"), status.HTTP_200_OK],
        [pytest.lazy_fixture("active_campaign"), status.HTTP_200_OK],
        [pytest.lazy_fixture("completed_campaign"), status.HTTP_200_OK],
    ],
)
def test_get_level_detail_public(
    campaign: Campaign,
    setup_product,
    expected_status: int,
):
    """Ensure API returns correct data."""
    category = ProductCategoryFactory(campaign=campaign)
    product = ProductFactory(category=category)
    test_level_data = TestLevelData(
        level_info={"cost": 100},
        total_count=10,
        sold_count=4,
        declined_count=1,
    )
    setup_product(product, [test_level_data])
    level = Level.objects.filter(product_id=product.id).first()
    api_client = test.APIClient()
    response = api_client.get(
        get_detail_level_url(kwargs={"pk": level.pk}),
        data={
            "chamber": category.campaign.chamber_id,
        },
    )

    assert response.status_code == expected_status, response.data

    response_data = response.data
    match_fields = (
        "id",
        "name",
        "cost",
        "description",
        "benefits",
        "conditions",
    )
    for field in match_fields:
        assert response_data[field] == getattr(level, field)
