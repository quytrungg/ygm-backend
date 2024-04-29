import typing
from decimal import Decimal

from django.urls import reverse_lazy
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

import pytest

from apps.campaigns import factories as cmp_factories
from apps.campaigns import models as cmp_models
from apps.members import factories as mbr_factories
from apps.members import models as mbr_models

from ..conftest import ContractLevelData


def get_purchasing_member_url(action: str, kwargs=None) -> typing.Any:
    """Return url of member APIs."""
    return reverse_lazy(
        f"v1:public:purchasing-members-{action}",
        kwargs=kwargs,
    )


def get_level_purchasing_member_url(action: str, kwargs=None) -> typing.Any:
    """Return url of member APIs."""
    return reverse_lazy(
        f"v1:volunteer:purchasing-levels-{action}",
        kwargs=kwargs,
    )


list_purchasing_member_url = get_purchasing_member_url(action="list")
total_earnings_purchasing_member_url = get_purchasing_member_url(
    action="get-total-earnings",
)
list_level_purchasing_member_url = get_level_purchasing_member_url(
    action="list",
)


@pytest.fixture
def setup_member_contract(
    active_campaign: cmp_models.Campaign,
) -> typing.Callable:
    """Return factory function to set up contract's data."""
    def _setup(
        level_data: typing.Iterable[ContractLevelData],
        member: mbr_models.Member,
    ) -> mbr_models.Contract:
        """Set up contract's data."""
        _contract = mbr_factories.ContractFactory(
            campaign=active_campaign,
            member=member,
            approved_at=timezone.now(),
            status=mbr_models.Contract.STATUSES.APPROVED,
        )
        category = cmp_factories.ProductCategoryFactory(
            campaign=active_campaign,
        )
        product = cmp_factories.ProductFactory(category=category)
        for data in level_data:
            level = cmp_factories.LevelFactory(
                product=product,
                cost=data["cost"],
            )
            declined_at = timezone.now() if data["is_declined"] else None
            _ = cmp_models.LevelInstance.objects.create(
                level=level,
                cost=level.cost,
                declined_at=declined_at,
                contract=_contract,
            )
        return _contract
    return _setup


@pytest.fixture
def contracts(
    setup_member_contract: typing.Callable,
    members: list[mbr_models.Member],
) -> list[mbr_models.Contract]:
    """Create a contract with attached to member."""
    contract_list = []
    for member in members:
        contract_list.append(
            setup_member_contract(
                [
                    ContractLevelData(cost=Decimal(100), is_declined=False),
                    ContractLevelData(cost=Decimal(200), is_declined=False),
                ],
                member,
            ),
        )
    return contract_list


def test_purchasing_member_list_api(
    api_client: APIClient,
    contracts: list[mbr_models.Contract],
    members: list[mbr_models.Member],
) -> None:
    """Ensure purchasing member list API works properly with correct data."""
    response = api_client.get(
        list_purchasing_member_url,
        data={
            "chamber": contracts[0].campaign.chamber_id,
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.data
    assert len(response.data["results"]) == len(members)


def test_purchasing_member_total_earnings_api(
    api_client: APIClient,
    contracts: list[mbr_models.Contract],
    members: list[mbr_models.Member],
) -> None:
    """Ensure purchasing member list API works properly with correct data."""
    response = api_client.get(
        total_earnings_purchasing_member_url,
        data={
            "chamber": contracts[0].campaign.chamber_id,
        },
    )
    member_response = api_client.get(
        list_purchasing_member_url,
        data={
            "chamber": contracts[0].campaign.chamber_id,
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.data
    assert response.data["total_earnings"] == sum(
        member["total_spent"] for member in member_response.data["results"]
    )
    assert response.data["total_earnings"] > 0


def test_member_purchased_level_list_api(
    api_client: APIClient,
    contracts: list[mbr_models.Contract],
) -> None:
    """Ensure purchasing member list API works properly with correct data."""
    response = api_client.get(
        reverse_lazy("v1:public:purchased-levels-list"),
        data={
            "chamber": contracts[0].campaign.chamber_id,
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.data
