from functools import partial

from django.urls import reverse_lazy

from rest_framework import status, test

import pytest

from apps.campaigns.constants import CampaignStatus
from apps.campaigns.factories import CampaignFactory
from apps.campaigns.models import Campaign
from apps.chambers.models import Chamber
from apps.core.test_utils import CAAPIClient
from apps.incentives.constants import (
    IncentiveQualifierAmount,
    IncentiveQualifierName,
)
from apps.incentives.factories import IncentiveFactory
from apps.incentives.models import Incentive
from apps.users.factories import UserFactory
from apps.users.models import User


def get_incentive_url(action: str, kwargs=None):
    """Return url of contract api with kwargs."""
    return reverse_lazy(f"v1:chamber:incentive-{action}", kwargs=kwargs)


get_incentive_list_url = partial(get_incentive_url, action="list")
get_incentive_detail_url = partial(get_incentive_url, action="detail")
get_incentive_reorder_url = partial(get_incentive_url, action="reorder")
get_incentive_qualifier_amounts_url = partial(
    get_incentive_url,
    action="get-qualifier-amounts",
)
get_incentive_qualifier_names_url = partial(
    get_incentive_url,
    action="get-qualifier-names",
)


@pytest.fixture
def campaign(chamber) -> Campaign:
    """Return an open campaign within the chamber."""
    return CampaignFactory(chamber=chamber, status=CampaignStatus.CREATED)


@pytest.fixture
def incentives(campaign) -> list[Incentive]:
    """Return a list of incentives within the campaign."""
    return IncentiveFactory.create_batch(5, campaign=campaign)


def test_incentive_list_api(
    chamber_admin: User,
    incentives: list[Incentive],
) -> None:
    """Ensure that chamber admin can list incentives."""
    api_client = CAAPIClient()
    api_client.select_campaign(incentives[0].campaign)
    api_client.force_authenticate(user=chamber_admin)
    response = api_client.get(get_incentive_list_url())
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data.get("results")) == len(incentives)


def test_incentive_list_api_non_admin(campaign: Campaign) -> None:
    """Ensure that non-admin user cannot list incentives."""
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(user=UserFactory())
    response = api_client.get(get_incentive_list_url())
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_incentive_create_api(
    chamber_admin: User,
    chamber: Chamber,
    campaign: Campaign,
    incentive_data: dict,
) -> None:
    """Ensure that chamber admin can create incentives."""
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(user=chamber_admin)
    response = api_client.post(get_incentive_list_url(), data=incentive_data)
    assert response.status_code == status.HTTP_201_CREATED


def test_incentive_detail_api(
    chamber_admin: User,
    incentive: Incentive,
) -> None:
    """Ensure that chamber admin can access the incentive detail."""
    url = get_incentive_detail_url(kwargs={"pk": incentive.id})
    api_client = CAAPIClient()
    api_client.select_campaign(incentive.campaign)
    api_client.force_authenticate(user=chamber_admin)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_incentive_detail_api_non_admin(
    incentive: Incentive,
) -> None:
    """Ensure that non-admin user cannot access the incentive detail."""
    url = get_incentive_detail_url(kwargs={"pk": incentive.id})
    api_client = CAAPIClient()
    api_client.select_campaign(incentive.campaign)
    api_client.force_authenticate(user=UserFactory())
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_incentive_update_api(
    chamber_admin: User,
    incentive: Incentive,
    incentive_data: dict,
) -> None:
    """Ensure that chamber admin can update the incentive."""
    url = get_incentive_detail_url(kwargs={"pk": incentive.id})
    api_client = CAAPIClient()
    api_client.select_campaign(incentive.campaign)
    api_client.force_authenticate(user=chamber_admin)
    incentive_data["name"] = "Updated Name"
    response = api_client.put(url, data=incentive_data)
    assert response.status_code == status.HTTP_200_OK


def test_get_qualifier_amount_list_api(
    chamber_admin: User,
) -> None:
    """Ensure that chamber admin can get the list of qualifier amounts."""
    api_client = CAAPIClient()
    api_client.force_authenticate(user=chamber_admin)
    response = api_client.get(get_incentive_qualifier_amounts_url())
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == len(IncentiveQualifierAmount.choices)


def test_get_qualifier_name_list_api(
    chamber_admin: User,
) -> None:
    """Ensure that chamber admin can get the list of qualifier names."""
    api_client = CAAPIClient()
    api_client.force_authenticate(user=chamber_admin)
    response = api_client.get(get_incentive_qualifier_names_url())
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == len(IncentiveQualifierName.choices)


def test_get_qualifier_amount_list_api_non_admin(
    api_client: test.APIClient,
) -> None:
    """Ensure non-admin user can't access the list of qualifier amounts."""
    api_client.force_authenticate(user=UserFactory())
    response = api_client.get(get_incentive_qualifier_amounts_url())
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_qualifier_name_list_api_non_admin(
    api_client: test.APIClient,
) -> None:
    """Ensure non-admin user can't access the list of qualifier names."""
    api_client.force_authenticate(user=UserFactory())
    response = api_client.get(get_incentive_qualifier_names_url())
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_incentive_reorder_api(
    chamber_admin: User,
    campaign: Campaign,
) -> None:
    """Ensure CA can reorder item in incentive list data to new index."""
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(chamber_admin)
    _incentives = IncentiveFactory.create_batch(size=5, campaign=campaign)
    incentive = _incentives[0]
    orders = list(range(len(_incentives)))
    assert [incentive.order for incentive in _incentives] == orders
    response = api_client.put(
        get_incentive_reorder_url(kwargs={"pk": incentive.pk}),
        data={"order": len(_incentives) - 1},
    )
    assert response.status_code == status.HTTP_200_OK
    for incentive in _incentives:
        incentive.refresh_from_db()
    assert [incentive.order for incentive in _incentives] == (
        orders[-1:] + orders[:-1]
    )


def test_incentive_reorder_api_fail(
    chamber_admin: User,
    campaign: Campaign,
) -> None:
    """Ensure category's order stays the same if request order is too big."""
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(chamber_admin)
    _incentives = IncentiveFactory.create_batch(
        size=5,
        campaign=campaign,
    )
    incentive = _incentives[0]
    response = api_client.put(
        get_incentive_reorder_url(kwargs={"pk": incentive.pk}),
        data={"order": len(_incentives)},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
