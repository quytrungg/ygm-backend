from functools import partial

from django.urls import reverse_lazy
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

import pytest

from apps.campaigns.constants import UserCampaignRole
from apps.campaigns.factories import (
    LevelFactory,
    LevelInstanceFactory,
    ProductCategoryFactory,
    ProductFactory,
    UserCampaignFactory,
)
from apps.campaigns.models import Campaign, LevelInstance, UserCampaign
from apps.chambers.models import StoredMember
from apps.core.test_utils import CAAPIClient
from apps.members.factories import ContractFactory
from apps.members.models import Contract, ContractCreditInfo, Invoice
from apps.users.models import User


def get_contract_url(action: str, kwargs=None):
    """Return url of contract api with kwargs."""
    return reverse_lazy(f"v1:chamber:contract-{action}", kwargs=kwargs)


def get_volunteer_contract_url(action: str, kwargs=None):
    """Return contract urls for volunteer namespace."""
    return reverse_lazy(
        f"v1:volunteer:public-contract-{action}",
        kwargs=kwargs,
    )


def get_public_contract_url(action: str, kwargs=None):
    """Return url of public contracts."""
    return reverse_lazy(f"v1:public:contract-{action}", kwargs=kwargs)


get_list_contract_url = partial(get_contract_url, action="list")()
get_detail_contract_url = partial(get_contract_url, action="detail")
get_approve_contract_url = partial(get_contract_url, action="approve")
get_decline_contract_url = partial(get_contract_url, action="decline")
get_reassign_contract_url = partial(get_contract_url, action="reassign")
get_sign_public_contract_url = partial(get_public_contract_url, action="sign")
get_detail_public_contract_url = partial(
    get_public_contract_url,
    action="detail",
)


@pytest.fixture
def ca_campaign_user(contract: Contract, chamber_admin: User) -> UserCampaign:
    """Return CA campaign user."""
    return UserCampaignFactory(
        campaign=contract.campaign,
        role=UserCampaignRole.VOLUNTEER,
        user=chamber_admin,
    )


@pytest.fixture
def chamber_chair_user(contract: Contract) -> UserCampaign:
    """Return chamber chair user."""
    return UserCampaignFactory(
        campaign=contract.campaign,
        role=UserCampaignRole.CHAMBER_CHAIR,
    )


# pylint: disable=unused-variable
def test_contract_list_api(
    chamber_admin: User,
    active_campaign: Campaign,
    contracts: list[Contract],
) -> None:
    """Ensure chamber admin can view list of contracts from api."""
    user_campaign = UserCampaignFactory(
        user_id=chamber_admin.id,
        campaign_id=active_campaign.id,
    )
    contract = ContractFactory(    # noqa: F841
        created_by_id=user_campaign.id,
        campaign_id=active_campaign.id,
    )
    api_client = CAAPIClient()
    api_client.select_campaign(active_campaign)
    api_client.force_authenticate(chamber_admin)
    response = api_client.get(get_list_contract_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == len(contracts) + 1


@pytest.mark.parametrize(
    ["contract", "expected_status"],
    [
        [pytest.lazy_fixture("draft_contract"), status.HTTP_204_NO_CONTENT],
        [pytest.lazy_fixture("approved_contract"), status.HTTP_403_FORBIDDEN],
    ],
)
def test_contract_delete_api(
    chamber_admin_client: CAAPIClient,
    contract: Contract,
    expected_status: int,
):
    """Ensure only draft contracts can be deleted, else raise 403 error."""
    chamber_admin_client.select_campaign(contract.campaign)
    response = chamber_admin_client.delete(
        get_detail_contract_url(
            kwargs={"pk": contract.pk},
        ),
    )
    assert response.status_code == expected_status


def test_public_contract_detail_api(
    api_client: APIClient,
    active_campaign: Campaign,
) -> None:
    """Ensure that everyone can access public info of a contract."""
    contract = ContractFactory(
        campaign=active_campaign,
        status=Contract.STATUSES.SIGNED,
        signature=active_campaign.name,
        signed_at=timezone.now(),
    )
    response = api_client.get(
        get_detail_public_contract_url(kwargs={"token": contract.token}),
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    argnames=["campaign", "expected_status"],
    argvalues=[
        [pytest.lazy_fixture("open_campaign"), status.HTTP_403_FORBIDDEN],
        [pytest.lazy_fixture("active_campaign"), status.HTTP_200_OK],
        [pytest.lazy_fixture("completed_campaign"), status.HTTP_403_FORBIDDEN],
    ],
)
def test_contract_approve_api(
    chamber_admin_client: CAAPIClient,
    campaign,
    expected_status: int,
):
    """Ensure contract can be approved."""
    category = ProductCategoryFactory(campaign=campaign)
    product = ProductFactory(category=category)
    level = LevelFactory(product=product, amount=2)
    contract = ContractFactory(
        campaign=campaign,
        status=Contract.STATUSES.SIGNED,
    )
    level_instance = LevelInstance.from_level(level)
    level_instance.contract = contract
    level_instance.save()
    chamber_stored_members = StoredMember.objects.filter(
        chamber_id=campaign.chamber_id,
    )
    prev_stored_member_count = chamber_stored_members.count()
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.post(
        get_approve_contract_url(
            kwargs={"pk": contract.pk},
        ),
        data={
            "selected_level_ids": contract.levels.values_list("id", flat=True),
        },
    )
    assert response.status_code == expected_status, response.data
    if response.status_code == status.HTTP_200_OK:
        contract.refresh_from_db()
        assert contract.status == Contract.STATUSES.APPROVED
        assert chamber_stored_members.count() == prev_stored_member_count + 1
        assert Invoice.objects.filter(
            name=contract.name,
            contract_id=contract.id,
            sent_at__isnull=True,
            is_paid=False,
        ).count() == 1


@pytest.mark.parametrize(
    argnames=["campaign", "expected_status"],
    argvalues=[
        [pytest.lazy_fixture("open_campaign"), status.HTTP_403_FORBIDDEN],
        [pytest.lazy_fixture("active_campaign"), status.HTTP_200_OK],
        [pytest.lazy_fixture("completed_campaign"), status.HTTP_403_FORBIDDEN],
    ],
)
def test_contract_decline_api(
    chamber_admin_client: CAAPIClient,
    campaign,
    expected_status: int,
):
    """Ensure contract can be declined."""
    contract = ContractFactory(
        campaign=campaign,
        status=Contract.STATUSES.SIGNED,
    )
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.post(
        get_decline_contract_url(
            kwargs={"pk": contract.pk},
        ),
    )
    assert response.status_code == expected_status
    if response.status_code == status.HTTP_200_OK:
        contract.refresh_from_db()
        assert contract.status == Contract.STATUSES.DECLINED


@pytest.mark.parametrize(
    ["contract", "expected_status"],
    [
        [pytest.lazy_fixture("draft_contract"), status.HTTP_200_OK],
        [pytest.lazy_fixture("approved_contract"), status.HTTP_200_OK],
    ],
)
def test_contract_detail_api(
    chamber_admin: User,
    contract: Contract,
    expected_status: int,
) -> None:
    """Ensure that contract detail API works as expected."""
    api_client = CAAPIClient()
    api_client.select_campaign(contract.campaign)
    api_client.force_authenticate(chamber_admin)
    response = api_client.get(
        get_detail_contract_url(kwargs={"pk": contract.pk}),
    )
    assert response.status_code == expected_status


@pytest.mark.skip(reason="Skip due to new logic")
def test_public_contract_sign_api(
    api_client: APIClient,
    active_campaign: Campaign,
) -> None:
    """Ensure unregistered users can sign an available public contract."""
    contract = ContractFactory(
        campaign=active_campaign,
        status=Contract.STATUSES.SENT,
    )
    instances = LevelInstanceFactory.create_batch(size=3, contract=contract)
    response = api_client.post(
        get_sign_public_contract_url(kwargs={"token": contract.token}),
        data={
            "signature": "Contract Signature",
            "level_ids": [instance.id for instance in instances[:2]],
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    contract.refresh_from_db()
    for instance in instances:
        instance.refresh_from_db()
    assert contract.status == Contract.STATUSES.SIGNED
    assert contract.signed_at
    assert contract.signature
    assert all(not instance.declined_at for instance in instances[:2])
    assert instances[2].declined_at


def test_public_contract_sign_api_fail(
    api_client: APIClient,
    active_campaign: Campaign,
) -> None:
    """Ensure signed public contract cannot be signed again."""
    contract = ContractFactory(
        campaign=active_campaign,
        status=Contract.STATUSES.SIGNED,
        signature=active_campaign.name,
        signed_at=timezone.now(),
    )
    instances = LevelInstanceFactory.create_batch(size=3, contract=contract)
    response = api_client.post(
        get_sign_public_contract_url(kwargs={"token": contract.token}),
        data={
            "signature": "Contract Signature",
            "level_ids": [instance.id for instance in instances[:2]],
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_reassign_contract_api(
    chamber_admin: User,
    contract: Contract,
    user_campaign: UserCampaign,
) -> None:
    """Ensure CA can reassign contract to another campaign user."""
    api_client = CAAPIClient()
    api_client.select_campaign(contract.campaign)
    api_client.force_authenticate(chamber_admin)
    reassigned_user = UserCampaignFactory(
        role=UserCampaignRole.VOLUNTEER,
        campaign=contract.campaign,
    )
    credits_info = ContractCreditInfo.objects.create(
        contract=contract,
        user_campaign=user_campaign,
        portion=1,
    )
    response = api_client.post(
        get_reassign_contract_url(),
        data=[{"contract": contract.id, "user": reassigned_user.id}],
    )
    assert response.status_code == status.HTTP_200_OK, response.data
    assert ContractCreditInfo.objects.filter(
        contract=credits_info.contract,
        user_campaign=reassigned_user,
        portion=credits_info.portion,
    ).exists()
    contract.refresh_from_db()
    assert contract.created_by == reassigned_user
    assert contract.shared_credits_with.filter(id=reassigned_user.id).exists()
    assert not contract.shared_credits_with.filter(
        id=user_campaign.id,
    ).exists()


@pytest.mark.parametrize(
    argnames="reassigned_user",
    argvalues=[
        pytest.lazy_fixture("ca_campaign_user"),
        pytest.lazy_fixture("chamber_chair_user"),
    ],
)
def test_reassign_contract_invalid_campaign_user(
    chamber_admin: User,
    contract: Contract,
    reassigned_user: UserCampaign,
) -> None:
    """Ensure CA cannot reassign contract to CA or chamber chair users."""
    api_client = CAAPIClient()
    api_client.select_campaign(contract.campaign)
    api_client.force_authenticate(chamber_admin)
    response = api_client.post(
        get_reassign_contract_url(),
        data=[{"contract": contract.id, "user": reassigned_user.id}],
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
