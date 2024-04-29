# pylint: disable=unused-argument,too-many-arguments

from functools import partial

from django.urls import reverse_lazy

from rest_framework import status, test

import pytest

from apps.campaigns.constants import DEFAULT_PRODUCT_CATEGORIES
from apps.campaigns.factories import (
    ProductAttachmentFactory,
    ProductCategoryFactory,
    ProductFactory,
)
from apps.campaigns.models import (
    Campaign,
    Level,
    LevelInstance,
    Product,
    ProductAttachment,
    ProductCategory,
)
from apps.core.test_utils import CAAPIClient, TestLevelData, get_test_file_url


def get_product_category_url(action_name: str, kwargs=None):
    """Return url for chamber admin product category's APIs."""
    return reverse_lazy(
        f"v1:chamber:product-category-{action_name}",
        kwargs=kwargs,
    )


get_list_product_category_url = partial(
    get_product_category_url,
    action_name="list",
)
get_detail_product_category_url = partial(
    get_product_category_url,
    action_name="detail",
)
get_category_statistics_url = partial(
    get_product_category_url,
    action_name="get-stats",
)
get_quick_update_product_category_url = partial(
    get_product_category_url,
    action_name="update-name",
)
get_category_reorder_url = partial(
    get_product_category_url,
    action_name="reorder",
)
get_category_duplicate_url = partial(
    get_product_category_url,
    action_name="duplicate",
)


@pytest.mark.parametrize(
    argnames=["campaign", "expected_count"],
    argvalues=[
        [
            pytest.lazy_fixture("open_campaign"),
            3 + len(DEFAULT_PRODUCT_CATEGORIES),
        ],
        [
            pytest.lazy_fixture("active_campaign"),
            3 + len(DEFAULT_PRODUCT_CATEGORIES),
        ],
        [
            pytest.lazy_fixture("completed_campaign"),
            3 + len(DEFAULT_PRODUCT_CATEGORIES),
        ],
    ],
)
def test_get_product_category_list(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
    expected_count: int,
    product_categories: list[ProductCategory],
):
    """Ensure categories list can be retrieved."""
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.get(get_list_product_category_url())
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
def test_get_product_category_detail(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
    product_category: ProductCategory,
):
    """Ensure category's detail can be retrieved."""
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.get(
        get_detail_product_category_url(
            kwargs={"pk": product_category.pk},
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
def test_update_product_category(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
    expected_status: int,
    product_category: ProductCategory,
    create_file,
):
    """Ensure category can be updated only if campaign is open."""
    update_data = {
        "name": product_category.name + "s",
        "image": None,
        "background_color": "FFFFFF",
    }
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.put(
        get_detail_product_category_url(
            kwargs={"pk": product_category.pk},
        ),
        data=update_data,
    )
    assert response.status_code == expected_status
    if response.status_code == status.HTTP_200_OK:
        product_category.refresh_from_db()
        assert product_category.name == update_data["name"]


@pytest.mark.parametrize(
    argnames=["campaign", "expected_status"],
    argvalues=[
        [pytest.lazy_fixture("open_campaign"), status.HTTP_204_NO_CONTENT],
        [pytest.lazy_fixture("active_campaign"), status.HTTP_403_FORBIDDEN],
        [pytest.lazy_fixture("completed_campaign"), status.HTTP_403_FORBIDDEN],
    ],
)
def test_delete_product_category(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
    expected_status: int,
    product_category: ProductCategory,
):
    """Ensure category can be deleted only if campaign is open."""
    product_category_pk = product_category.pk
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.delete(
        get_detail_product_category_url(kwargs={"pk": product_category.pk}),
    )
    assert response.status_code == expected_status
    if response.status_code == status.HTTP_204_NO_CONTENT:
        assert not ProductCategory.objects.filter(
            pk=product_category_pk,
        ).exists()


@pytest.mark.parametrize(
    argnames=["campaign", "expected_status"],
    argvalues=[
        [pytest.lazy_fixture("open_campaign"), status.HTTP_201_CREATED],
        [pytest.lazy_fixture("active_campaign"), status.HTTP_403_FORBIDDEN],
        [pytest.lazy_fixture("completed_campaign"), status.HTTP_403_FORBIDDEN],
    ],
)
def test_create_product_category(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
    expected_status: int,
    create_file,
):
    """Ensure category can be created only if campaign is open."""
    creation_data = {
        "name": "test_category",
        "image": get_test_file_url(create_file("test.png")),
        "background_color": "",
    }
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.post(
        get_list_product_category_url(),
        data=creation_data,
    )
    assert response.status_code == expected_status
    if response.status_code == status.HTTP_201_CREATED:
        new_category = ProductCategory.objects.get(id=response.data["id"])
        assert new_category.campaign_id == campaign.id
        assert new_category.name == creation_data["name"]


@pytest.mark.skip(reason="Skip due to new logic")
def test_get_category_statistics_api(
    product_category: ProductCategory,
    product: Product,
    level: Level,
    level_instances: list[LevelInstance],
    chamber_admin_client: test.APIClient,
) -> None:
    """Ensure CA can get product category's statistics from API."""
    response = chamber_admin_client.get(
        get_category_statistics_url(kwargs={"pk": product_category.pk}),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["total_value"] == level.cost * len(level_instances)


def test_product_category_update_name_api(
    product_category: ProductCategory,
    chamber_admin_client: CAAPIClient,
) -> None:
    """Ensure CA can update product category's name."""
    updated_name = f"new {product_category.name}"
    chamber_admin_client.select_campaign(campaign=product_category.campaign)
    response = chamber_admin_client.put(
        get_quick_update_product_category_url(
            kwargs={"pk": product_category.pk},
        ),
        data={"name": updated_name},
    )
    assert response.status_code == status.HTTP_200_OK
    product_category.refresh_from_db()
    assert product_category.name == updated_name


def test_product_category_update_name_api_fail(
    campaign: Campaign,
    chamber_admin_client: CAAPIClient,
    product_category: ProductCategory,
) -> None:
    """Ensure CA can't update category of another campaign."""
    another_product_category = ProductCategoryFactory(campaign=campaign)
    chamber_admin_client.select_campaign(product_category.campaign)
    response = chamber_admin_client.put(
        get_quick_update_product_category_url(
            kwargs={"pk": another_product_category.pk},
        ),
        data={"name": f"new{another_product_category.name}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_category_reorder_api(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
) -> None:
    """Ensure CA can reorder product category to new index."""
    product_categories = list(
        ProductCategory.objects.filter(campaign=campaign),
    )
    category = product_categories[0]
    orders = list(range(len(product_categories)))
    assert [category.order for category in product_categories] == orders
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.put(
        get_category_reorder_url(kwargs={"pk": category.pk}),
        data={"order": len(product_categories) - 1},
    )
    assert response.status_code == status.HTTP_200_OK
    for category in product_categories:
        category.refresh_from_db()
    assert [category.order for category in product_categories] == (
        orders[-1:] + orders[:-1]
    )


def test_category_reorder_api_fail(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
) -> None:
    """Ensure category's order stays the same if request order is too big."""
    product_categories = list(
        ProductCategory.objects.filter(campaign=campaign),
    )
    category = product_categories[0]
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.put(
        get_category_reorder_url(kwargs={"pk": category.pk}),
        data={"order": len(product_categories)},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_category_duplicate_api(
    chamber_admin_client: CAAPIClient,
    product_category: ProductCategory,
    setup_product,
):
    """Ensure category/products/levels/attachments is duplicated."""
    product = ProductFactory(category=product_category)
    ProductAttachmentFactory.create_batch(
        size=2,
        product=product,
    )
    levels_data = [
        TestLevelData({"name": "L1"}, total_count=2),
        TestLevelData({"name": "L2"}, total_count=3),
    ]
    setup_product(product, levels_data)
    prev_max_order = ProductCategory.objects.filter(
        campaign=product_category.campaign,
    ).get_max_order()
    chamber_admin_client.select_campaign(product_category.campaign)
    response = chamber_admin_client.post(
        get_category_duplicate_url(kwargs={"pk": product_category.pk}),
    )
    data = response.data
    assert response.status_code == status.HTTP_200_OK, data
    new_category = ProductCategory.objects.filter(id=data["id"]).first()
    assert new_category
    assert new_category.order == prev_max_order + 1
    assert Product.objects.filter(category_id=new_category.id).count() == 1
    assert ProductAttachment.objects.filter(
        product__category_id=new_category.id,
    ).count() == 2
    assert (
        Level.objects.filter(product__category_id=new_category.id).count()
        == len(levels_data)
    )
