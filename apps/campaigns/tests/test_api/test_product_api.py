# pylint: disable=unused-argument,too-many-arguments

from functools import partial

from django.urls import reverse_lazy

from rest_framework import status

import pytest

from apps.campaigns.factories import (
    ProductAttachmentFactory,
    ProductCategoryFactory,
    ProductFactory,
)
from apps.campaigns.models import (
    Campaign,
    Level,
    Product,
    ProductAttachment,
    ProductCategory,
)
from apps.core.test_utils import CAAPIClient, TestLevelData, get_test_file_url


def get_product_url(action_name: str, kwargs=None):
    """Return url for chamber admin product's APIs."""
    return reverse_lazy(
        f"v1:chamber:product-{action_name}",
        kwargs=kwargs,
    )


get_list_product_url = partial(
    get_product_url,
    action_name="list",
)
get_detail_product_url = partial(
    get_product_url,
    action_name="detail",
)
get_product_duplicate_url = partial(
    get_product_url,
    action_name="duplicate",
)
get_product_reorder_url = partial(get_product_url, action_name="reorder")


@pytest.fixture
def product_category(campaign: Campaign) -> ProductCategory:
    """Return a test product category."""
    return ProductCategoryFactory(campaign=campaign)


@pytest.fixture
def products(product_category: ProductCategory) -> list[Product]:
    """Return list of products for testing."""
    return ProductFactory.create_batch(3, category=product_category)


@pytest.fixture
def product(product_category: ProductCategory) -> Product:
    """Return a test product."""
    return ProductFactory(category=product_category)


@pytest.mark.parametrize(
    argnames=["campaign", "expected_count"],
    argvalues=[
        [pytest.lazy_fixture("open_campaign"), 3],
        [pytest.lazy_fixture("active_campaign"), 3],
        [pytest.lazy_fixture("completed_campaign"), 3],
    ],
)
def test_get_product_list(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
    expected_count: int,
    products: list[Product],
):
    """Ensure product list can be retrieved."""
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.get(get_list_product_url())
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
def test_get_product_detail(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
    product: Product,
):
    """Ensure product detail can be retrieved."""
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.get(
        get_detail_product_url(
            kwargs={"pk": product.pk},
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
def test_update_product(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
    expected_status: int,
    product: Product,
    create_file,
    django_db_blocker,
):
    """Ensure product can be updated only if campaign is open."""
    with django_db_blocker.unblock():
        another_category = ProductCategoryFactory(campaign=campaign)
    update_data = {
        "category": another_category.id,
        "name": product.name + "s",
        "is_included_in_renewal": product.is_included_in_renewal,
        "pre_trc_income": product.pre_trc_income,
        "description": product.description,
        "attachments": [
            {
                "name": "cat.mp4",
                "file": get_test_file_url(create_file("cat.mp4")),
                "external_url": "",
                "content_type": "video/mp4",
            },
            {
                "name": "cat.png",
                "file": None,
                "external_url": "https://www.youtube.com/embed/AAAAABBBBBC",
                "content_type": "image/png",
            },
        ],
    }
    assert product.attachments.count() == 0
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.put(
        get_detail_product_url(
            kwargs={"pk": product.pk},
        ),
        data=update_data,
    )
    assert response.status_code == expected_status
    if response.status_code == status.HTTP_200_OK:
        product.refresh_from_db()
        assert product.name == update_data["name"]
        assert product.attachments.count() == len(update_data["attachments"])


@pytest.mark.parametrize(
    argnames=["campaign", "expected_status"],
    argvalues=[
        [pytest.lazy_fixture("open_campaign"), status.HTTP_204_NO_CONTENT],
        [pytest.lazy_fixture("active_campaign"), status.HTTP_403_FORBIDDEN],
        [pytest.lazy_fixture("completed_campaign"), status.HTTP_403_FORBIDDEN],
    ],
)
def test_delete_product(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
    expected_status: int,
    product: Product,
):
    """Ensure product can be deleted only if campaign is open."""
    product_pk = product.pk
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.delete(
        get_detail_product_url(kwargs={"pk": product_pk}),
    )
    assert response.status_code == expected_status
    if response.status_code == status.HTTP_204_NO_CONTENT:
        assert not Product.objects.filter(pk=product_pk).exists()


@pytest.mark.parametrize(
    argnames=["campaign", "expected_status"],
    argvalues=[
        [pytest.lazy_fixture("open_campaign"), status.HTTP_201_CREATED],
        [pytest.lazy_fixture("active_campaign"), status.HTTP_403_FORBIDDEN],
        [pytest.lazy_fixture("completed_campaign"), status.HTTP_403_FORBIDDEN],
    ],
)
def test_create_product(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
    expected_status: int,
    create_file,
    product_category: ProductCategory,
):
    """Ensure product can be created only if campaign is open."""
    creation_data = {
        "category": product_category.id,
        "name": "test_product",
        "is_included_in_renewal": True,
        "pre_trc_income": 10,
        "description": "test",
        "attachments": [
            {
                "name": "cat.mp4",
                "file": get_test_file_url(create_file("cat.mp4")),
                "external_url": "",
                "content_type": "video/mp4",
            },
            {
                "name": "cat.png",
                "file": None,
                "external_url": "https://www.youtube.com/embed/AAAAABBBBBC",
                "content_type": "image/png",
            },
        ],
    }
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.post(
        get_list_product_url(),
        data=creation_data,
    )
    assert response.status_code == expected_status
    if response.status_code == status.HTTP_201_CREATED:
        new_product = Product.objects.get(id=response.data["id"])
        assert new_product.category_id == product_category.id
        assert new_product.name == creation_data["name"]


def test_product_duplicate_api(
    chamber_admin_client: CAAPIClient,
    product_category: ProductCategory,
    setup_product,
):
    """Ensure products/levels/attachments is duplicated."""
    _product = ProductFactory(category=product_category)
    ProductAttachmentFactory.create_batch(
        size=2,
        product=_product,
    )
    levels_data = [
        TestLevelData({"name": "L1"}, total_count=2),
        TestLevelData({"name": "L2"}, total_count=3),
    ]
    setup_product(_product, levels_data)
    chamber_admin_client.select_campaign(campaign=product_category.campaign)
    response = chamber_admin_client.post(
        get_product_duplicate_url(kwargs={"pk": _product.pk}),
    )
    data = response.data
    assert response.status_code == status.HTTP_200_OK, data
    new_product = Product.objects.filter(id=data["id"]).first()
    assert new_product
    assert ProductAttachment.objects.filter(
        product_id=new_product.id,
    ).count() == 2
    assert (
        Level.objects.filter(product_id=new_product.id).count()
        == len(levels_data)
    )


# pylint: disable=redefined-outer-name
def test_product_reorder_api(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
) -> None:
    """Ensure CA can reorder product to new index."""
    category = ProductCategoryFactory(campaign=campaign)
    ProductFactory.create_batch(size=10, category=category)
    products = list(Product.objects.filter(category=category))
    product = products[0]
    orders = list(range(len(products)))
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.put(
        get_product_reorder_url(kwargs={"pk": product.id}),
        data={"order": len(products) - 1},
    )
    assert response.status_code == status.HTTP_200_OK
    for product in products:
        product.refresh_from_db()
    assert [product.order for product in products] == orders[-1:] + orders[:-1]


# pylint: disable=redefined-outer-name
def test_product_reorder_api_fail(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
) -> None:
    """Ensure product's order stays the same if request order is too big."""
    ProductFactory.create_batch(size=10, category__campaign=campaign)
    products = list(Product.objects.filter(category__campaign=campaign))
    product = products[0]
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.put(
        get_product_reorder_url(kwargs={"pk": product.id}),
        data={"order": len(products)},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
