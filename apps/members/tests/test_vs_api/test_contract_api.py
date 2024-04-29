from functools import partial

from django.urls import reverse_lazy
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

import pytest

from apps.campaigns.constants import UserCampaignRole
from apps.campaigns.factories import (
    CampaignFactory,
    ProductCategoryFactory,
    ProductFactory,
    UserCampaignFactory,
)
from apps.campaigns.models import Campaign, Level, LevelInstance
from apps.chambers.factories import StoredMemberFactory
from apps.core.test_utils import TestLevelData
from apps.users.factories import VolunteerFactory
from apps.users.models import User

from ...models import Contract


def get_contract_url(action: str, kwargs=None):
    """Return url of contract API with kwargs for volunteer site."""
    return reverse_lazy(f"v1:volunteer:contract-{action}", kwargs=kwargs)


get_attach_level_url = partial(
    get_contract_url,
    action="attach-level",
)
get_contract_create_url = partial(
    get_contract_url,
    action="list",
)


def create_volunteer(campaign: Campaign, **kwargs):
    """Return a volunteer user."""
    user = VolunteerFactory(chamber=campaign.chamber)
    return UserCampaignFactory(user=user, campaign=campaign, **kwargs)


@pytest.fixture
def contract_creation_data():
    """Return contract creation data factory."""
    def _build_creation_data(**kwargs):
        """Return default contract creation data."""
        default_data = {
            "type": Contract.TYPES.CASH,
            "member": {
                "name": "Member",
                "address": "abcxyz",
                "city": "New York",
                "state": "NY",
                "zipcode": "12355",
                "first_name": "Mem",
                "last_name": "ber",
                "email": "member@gmail.com",
                "work_phone": "1234567891",
                "mobile_phone": "1987654321",
            },
            "status": Contract.STATUSES.SENT,
            "note": "",
            "levels": [],
            "shared_credits_with": [],
            "created_date": timezone.now().strftime("%m/%d/%Y"),
        }
        default_data.update(kwargs)
        return default_data
    return _build_creation_data


# pylint: disable=too-many-locals
def test_create_contract_successfully(
    api_client: APIClient,
    active_campaign: Campaign,
    contract_creation_data,
    setup_product,
):
    """Ensure contract is created successfully."""
    product_category = ProductCategoryFactory(campaign=active_campaign)
    product = ProductFactory(category=product_category)
    levels = setup_product(
        product,
        [
            TestLevelData({"name": "L1"}, total_count=2),
            TestLevelData({"name": "L2"}, total_count=2),
        ],
    )
    stored_member = StoredMemberFactory(chamber=active_campaign.chamber)
    volunteer = create_volunteer(
        active_campaign,
        role=UserCampaignRole.VOLUNTEER,
        member_id=stored_member.id,
    )
    shared_volunteers = [
        create_volunteer(active_campaign, member_id=stored_member.id)
        for _ in range(2)
    ]
    api_client.force_authenticate(volunteer.user)
    data = contract_creation_data(
        levels=[
            {"level_id": levels[0].id, "trade_with": "", "id": None},
            {"level_id": levels[1].id, "trade_with": "", "id": None},
        ],
        shared_credits_with=[
            shared_volunteer.id for shared_volunteer in shared_volunteers
        ],
    )
    data["member"]["stored_member_id"] = stored_member.id
    data["member"]["name"] = stored_member.name
    contract_name = f"{data['member']['name']} {data['created_date']}"
    duplicate_count = Contract.objects.filter(
        name__icontains=contract_name,
    ).count()
    if duplicate_count:
        contract_name = f"{contract_name} {duplicate_count}"
    response = api_client.post(get_contract_create_url(), data=data)
    assert response.status_code == status.HTTP_201_CREATED, response.data
    assert response.data["name"] == contract_name
    new_contract_id = response.data["id"]
    new_contract_level_ids = set(
        LevelInstance.objects.filter(
            contract_id=new_contract_id,
        ).values_list("level_id", flat=True),
    )
    assert new_contract_level_ids == {level.id for level in levels}
    assert (
        Contract.objects.get(id=new_contract_id).shared_credits_with.count()
        == len(shared_volunteers) + 1   # count creator also
    )


def test_chamber_admin_cannot_create_contract(
    chamber_admin: User,
    api_client: APIClient,
):
    """Ensure chamber chair are not allowed to create contract."""
    api_client.force_authenticate(chamber_admin)
    _campaign = CampaignFactory(
        chamber_id=chamber_admin.chamber_id,
        status=Campaign.STATUSES.LIVE,
    )
    UserCampaignFactory(
        campaign=_campaign,
        user=chamber_admin,
        email=chamber_admin.email,
    )

    response = api_client.post(get_contract_create_url(), data={})

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_chamber_chair_cannot_create_contract(
    active_campaign: Campaign,
    api_client: APIClient,
):
    """Ensure chamber chair are not allowed to create contract."""
    volunteer = create_volunteer(
        campaign=active_campaign,
        role=UserCampaignRole.CHAMBER_CHAIR,
    )
    api_client.force_authenticate(volunteer.user)

    response = api_client.post(get_contract_create_url(), data={})

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.skip(reason="Skip due to new logic")
def test_create_contract_mismatch_type(
    api_client: APIClient,
    active_campaign: Campaign,
    contract_creation_data,
    setup_product,
):
    """Ensure contract type and its levels trade info follow constraints."""
    product_category = ProductCategoryFactory(campaign=active_campaign)
    product = ProductFactory(category=product_category)
    levels = setup_product(
        product,
        [
            TestLevelData({"name": "L1"}, total_count=2),
            TestLevelData({"name": "L2"}, total_count=2),
        ],
    )
    volunteer = create_volunteer(active_campaign)
    api_client.force_authenticate(volunteer.user)
    data = contract_creation_data(
        levels=[
            {"level_id": levels[0].id, "trade_with": "a", "id": None},
            {"level_id": levels[1].id, "trade_with": "b", "id": None},
        ],
    )
    response = api_client.post(get_contract_create_url(), data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "type" in [error["attr"] for error in response.data["errors"]]


@pytest.mark.skip(reason="Skip due to new logic")
def test_create_contract_select_sold_out_level(
    api_client: APIClient,
    active_campaign: Campaign,
    contract_creation_data,
    setup_product,
):
    """Ensure contract can't be created if it selects sold-out levels."""
    product_category = ProductCategoryFactory(campaign=active_campaign)
    product = ProductFactory(category=product_category)
    levels = setup_product(
        product,
        [
            TestLevelData({"name": "L1"}, total_count=2),
            TestLevelData({"name": "L2"}, total_count=2, sold_count=2),
        ],
    )
    volunteer = create_volunteer(active_campaign)
    api_client.force_authenticate(volunteer.user)
    active_campaign.has_trades = True
    active_campaign.save()
    data = contract_creation_data(
        levels=[
            {"level_id": levels[0].id, "trade_with": "a", "id": None},
            {"level_id": levels[1].id, "trade_with": "b", "id": None},
        ],
        type=Contract.TYPES.TRADE,
    )
    response = api_client.post(get_contract_create_url(), data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.data
    error_fields = [error["attr"] for error in response.data["errors"]]
    assert "type" not in error_fields
    assert "levels.1.level_id" in error_fields


def test_attach_product_api(
    volunteer_client: APIClient,
    level: Level,
    contract: Contract,
    level_instances_with_contract: list[LevelInstance],
    level_instances_without_contract: list[LevelInstance],
) -> None:
    """Ensure volunteer who created the contract can attach product."""
    assert level.instances.all().filter(contract=None).count() == len(
        level_instances_without_contract,
    )
    response = volunteer_client.post(
        get_attach_level_url(kwargs={"pk": contract.pk}),
        data={"level": level.pk},
    )
    assert response.status_code == status.HTTP_200_OK, response.data


def test_attach_product_api_fail_created_by(
    another_volunteer_client: APIClient,
    level: Level,
    contract: Contract,
    level_instances_with_contract: list[LevelInstance],
    level_instances_without_contract: list[LevelInstance],
) -> None:
    """Ensure users who didn't create the contract cannot attach product."""
    assert level.instances.all().filter(contract=None).exists()
    response = another_volunteer_client.post(
        get_attach_level_url(kwargs={"pk": contract.pk}),
        data={"level": level.pk},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert level.instances.all().filter(contract=None).exists()


@pytest.mark.skip(reason="Skip due to new logic")
def test_attach_product_api_fail_no_product(
    volunteer_client: APIClient,
    level: Level,
    contract: Contract,
    level_instances_with_contract: list[LevelInstance],
) -> None:
    """Ensure users can't attach product if there are no products left."""
    assert not level.instances.all().filter(contract=None).exists()
    response = volunteer_client.post(
        get_attach_level_url(kwargs={"pk": contract.pk}),
        data={"level": level.pk},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_attach_product_api_fail_non_draft_contract(
    volunteer_client: APIClient,
    level: Level,
    contract: Contract,
    level_instances_with_contract: list[LevelInstance],
    level_instances_without_contract: list[LevelInstance],
) -> None:
    """Ensure users can't attach product to non-draft contracts."""
    contract.status = Contract.STATUSES.SIGNED
    contract.save()
    response = volunteer_client.post(
        get_attach_level_url(kwargs={"pk": contract.pk}),
        data={"level": level.pk},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
