from decimal import Decimal
from functools import partial

from django.urls import reverse_lazy

from rest_framework import status

import pytest

from apps.campaigns.models import Campaign, LevelInstance
from apps.core.test_utils import CAAPIClient
from apps.members.constants import ContractStatus
from apps.members.models import Contract


def get_level_instance_url(action: str, kwargs=None) -> str:
    """Return level instance url for chamber admin."""
    return reverse_lazy(f"v1:chamber:level-instance-{action}", kwargs=kwargs)


get_decline_product_url = partial(get_level_instance_url, action="decline")
get_detail_level_instance_url = partial(
    get_level_instance_url,
    action="detail",
)


@pytest.mark.parametrize(
    ["updated_cost", "status_code"],
    [
        [Decimal(1000), status.HTTP_200_OK],
        [Decimal(-1000), status.HTTP_400_BAD_REQUEST],
    ],
)
def test_update_level_instance_api(
    chamber_admin_client: CAAPIClient,
    level_instance: LevelInstance,
    updated_cost: Decimal,
    status_code: int,
) -> None:
    """Ensure chamber admin can update cost of level instance/product."""
    chamber_admin_client.select_campaign(
        campaign=level_instance.level.product.category.campaign,
    )
    response = chamber_admin_client.put(
        get_detail_level_instance_url(kwargs={"pk": level_instance.pk}),
        data={"cost": updated_cost},
    )
    assert response.status_code == status_code


def test_decline_product_api(
    chamber_admin_client: CAAPIClient,
    level_instance: LevelInstance,
    signed_contract: Contract,
    active_campaign: Campaign,
) -> None:
    """Ensure chamber admin can decline a product."""
    chamber_admin_client.select_campaign(active_campaign)
    response = chamber_admin_client.post(
        get_decline_product_url(kwargs={"pk": level_instance.pk}),
    )
    assert response.status_code == status.HTTP_200_OK

    level_instance.refresh_from_db()
    signed_contract.refresh_from_db()
    assert level_instance.declined_at
    assert signed_contract.status == ContractStatus.DECLINED
    assert LevelInstance.objects.filter(
        level=level_instance.level,
        cost=level_instance.level.cost,
        contract=None,
    ).exists()


def test_decline_product_api_many(
    chamber_admin_client: CAAPIClient,
    level_instance: LevelInstance,
    level_instances: list[LevelInstance],
    signed_contract: Contract,
    active_campaign: Campaign,
):
    """Ensure decline product api works for contract with many products."""
    chamber_admin_client.select_campaign(active_campaign)
    for instance in level_instances:
        response = chamber_admin_client.post(
            get_decline_product_url(kwargs={"pk": instance.pk}),
        )
        assert response.status_code == status.HTTP_200_OK
        instance.refresh_from_db()
        signed_contract.refresh_from_db()
        assert instance.declined_at
        assert signed_contract.status == ContractStatus.SIGNED

    response = chamber_admin_client.post(
        get_decline_product_url(kwargs={"pk": level_instance.pk}),
    )
    assert response.status_code == status.HTTP_200_OK
    level_instance.refresh_from_db()
    signed_contract.refresh_from_db()
    assert level_instance.declined_at
    assert signed_contract.status == ContractStatus.DECLINED
    assert LevelInstance.objects.filter(
        level=level_instance.level,
        cost=level_instance.level.cost,
        contract=None,
    ).exists()
    for level_obj in level_instances:
        assert LevelInstance.objects.filter(
            level=level_obj.level,
            cost=level_obj.level.cost,
            contract=None,
        ).exists()
