# pylint: disable=unused-argument,too-many-arguments
from functools import partial

from django.urls import reverse_lazy

from rest_framework import status

import pytest

from apps.campaigns.factories import (
    LevelFactory,
    LevelInstanceFactory,
    ProductCategoryFactory,
    ProductFactory,
)
from apps.campaigns.models import (
    Campaign,
    Level,
    LevelInstance,
    Product,
    ProductCategory,
)
from apps.core.test_utils import CAAPIClient


def get_level_url(action_name: str, kwargs=None):
    """Return url for chamber admin level's APIs."""
    return reverse_lazy(
        f"v1:chamber:level-{action_name}",
        kwargs=kwargs,
    )


get_list_level_url = partial(
    get_level_url,
    action_name="list",
)
get_detail_level_url = partial(
    get_level_url,
    action_name="detail",
)
get_duplicate_level_url = partial(
    get_level_url,
    action_name="duplicate",
)
get_reorder_level_url = partial(get_level_url, action_name="reorder")


@pytest.mark.parametrize(
    argnames=["campaign", "expected_count"],
    argvalues=[
        [pytest.lazy_fixture("open_campaign"), 3],
        [pytest.lazy_fixture("active_campaign"), 3],
        [pytest.lazy_fixture("completed_campaign"), 3],
    ],
)
def test_get_level_list(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
    expected_count: int,
    levels: list[Level],
):
    """Ensure level list can be retrieved."""
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.get(get_list_level_url())
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == expected_count


@pytest.mark.parametrize(
    argnames="campaign",
    argvalues=[
        pytest.lazy_fixture("open_campaign"),
        pytest.lazy_fixture("active_campaign"),
        pytest.lazy_fixture("completed_campaign"),
    ],
)
def test_get_level_detail(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
    level: Level,
):
    """Ensure level's detail can be retrieved."""
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.get(
        get_detail_level_url(
            kwargs={"pk": level.pk},
        ),
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    argnames=["campaign", "expected_status"],
    argvalues=[
        [pytest.lazy_fixture("open_campaign"), status.HTTP_200_OK],
        [pytest.lazy_fixture("active_campaign"), status.HTTP_200_OK],
        [pytest.lazy_fixture("completed_campaign"), status.HTTP_403_FORBIDDEN],
    ],
)
def test_update_level(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
    expected_status: int,
    level: Level,
    product_category: ProductCategory,
    create_file,
    django_db_blocker,
):
    """Ensure level can be updated only if campaign is open."""
    with django_db_blocker.unblock():
        another_product = ProductFactory(category=product_category)
        LevelInstanceFactory.create_batch(
            size=3,
            level=level,
        )
    update_data = {
        "product": another_product.id,
        "name": level.name + "s",
        "cost": 100,
        "amount": 10,
        "benefits": "good",
        "description": "...",
        "conditions": "...",
    }

    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.put(
        get_detail_level_url(
            kwargs={"pk": level.pk},
        ),
        data=update_data,
    )
    assert response.status_code == expected_status
    if response.status_code == status.HTTP_200_OK:
        level.refresh_from_db()
        assert level.name == update_data["name"]
        assert level.instances.count() != update_data["amount"]


@pytest.mark.parametrize(
    argnames=["campaign", "expected_status"],
    argvalues=[
        [pytest.lazy_fixture("open_campaign"), status.HTTP_204_NO_CONTENT],
        [pytest.lazy_fixture("active_campaign"), status.HTTP_403_FORBIDDEN],
        [pytest.lazy_fixture("completed_campaign"), status.HTTP_403_FORBIDDEN],
    ],
)
def test_delete_level(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
    expected_status: int,
    level: Level,
):
    """Ensure level can be deleted only if campaign is open."""
    level_pk = level.pk
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.delete(
        get_detail_level_url(kwargs={"pk": level_pk}),
    )
    assert response.status_code == expected_status
    if response.status_code == status.HTTP_204_NO_CONTENT:
        assert not Level.objects.filter(pk=level_pk).exists()


@pytest.mark.parametrize(
    argnames=["campaign", "expected_status"],
    argvalues=[
        [pytest.lazy_fixture("open_campaign"), status.HTTP_201_CREATED],
        [pytest.lazy_fixture("active_campaign"), status.HTTP_403_FORBIDDEN],
        [pytest.lazy_fixture("completed_campaign"), status.HTTP_403_FORBIDDEN],
    ],
)
def test_create_level(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
    expected_status: int,
    product: Product,
):
    """Ensure level can be created only if campaign is open."""
    creation_data = {
        "product": product.id,
        "name": "test level",
        "cost": 100,
        "amount": 10,
        "benefits": "good",
        "description": "...",
        "conditions": "...",
    }
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.post(
        get_list_level_url(),
        data=creation_data,
    )
    assert response.status_code == expected_status
    if response.status_code == status.HTTP_201_CREATED:
        new_level = Level.objects.get(id=response.data["id"])
        assert new_level.product_id == product.id
        assert new_level.name == creation_data["name"]


@pytest.mark.skip("Check why campaign changes status")
def test_level_duplicate_api(
    chamber_admin_client: CAAPIClient,
    level: Level,
    level_instances: list[LevelInstance],
) -> None:
    """Ensure CA can duplicate a level."""
    chamber_admin_client.select_campaign(
        campaign=level.product.category.campaign,
    )
    response = chamber_admin_client.post(
        get_duplicate_level_url(kwargs={"pk": level.id}),
    )
    data = response.data
    assert response.status_code == status.HTTP_200_OK, data
    assert data["product"] == level.product_id
    assert data["name"] == level.name
    assert data["description"] == level.description
    assert data["conditions"] == level.conditions


def test_level_reorder_api(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
) -> None:
    """Ensure CA can reorder level to new index."""
    category = ProductCategoryFactory(campaign=campaign)
    product = ProductFactory(category=category)
    LevelFactory.create_batch(size=10, product=product)
    levels = list(Level.objects.filter(product=product))
    level = levels[0]
    orders = list(range(len(levels)))
    chamber_admin_client.select_campaign(campaign=campaign)
    response = chamber_admin_client.put(
        get_reorder_level_url(kwargs={"pk": level.id}),
        data={"order": len(levels) - 1},
    )
    assert response.status_code == status.HTTP_200_OK
    for level in levels:
        level.refresh_from_db()
    assert [level.order for level in levels] == orders[-1:] + orders[:-1]


def test_level_reorder_api_fail(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
) -> None:
    """Ensure level's order stays the same if the request order is too big."""
    LevelFactory.create_batch(size=10, product__category__campaign=campaign)
    levels = list(Level.objects.filter(product__category__campaign=campaign))
    level = levels[0]
    chamber_admin_client.select_campaign(campaign=campaign)
    response = chamber_admin_client.put(
        get_reorder_level_url(kwargs={"pk": level.id}),
        data={"order": len(levels)},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
