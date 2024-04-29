import copy
from datetime import date

from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.test import APIClient

import factory
import pytest

from apps.campaigns.constants import CampaignStatus, UserCampaignRole
from apps.campaigns.factories import (
    CampaignFactory,
    LevelInstanceFactory,
    UserCampaignFactory,
)
from apps.campaigns.models import Campaign, Level, Product, ProductCategory
from apps.chambers.models import Chamber
from apps.core.test_utils import CAAPIClient
from apps.users.factories import UserFactory
from apps.users.models import User


def test_campaign_list_api(chamber_admin: User, api_client: APIClient) -> None:
    """Ensure that chamber admin user can access to campaign list API."""
    CampaignFactory.create_batch(size=5, chamber_id=chamber_admin.chamber_id)
    api_client.force_authenticate(chamber_admin)
    url = reverse_lazy("v1:chamber:campaign-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_campaign_list_api_non_chamber_admin(api_client: APIClient) -> None:
    """Ensure that non-admin users can't access to campaign list API."""
    user = UserFactory()
    api_client.force_authenticate(user)
    url = reverse_lazy("v1:chamber:campaign-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_campaign_create_api(
    super_admin: User,
    api_client: APIClient,
    campaign_create_data: dict,
) -> None:
    """Ensure that super admin can create campaign."""
    api_client.force_authenticate(super_admin)
    url = reverse_lazy("v1:super-admin:campaign-list")
    response = api_client.post(url, data=campaign_create_data)
    assert response.status_code == status.HTTP_201_CREATED


def test_campaign_create_api_non_super_admin(
    chamber_admin: User,
    api_client: APIClient,
    campaign_create_data: dict,
):
    """Ensure that non-super-admin users cannot create campaign."""
    api_client.force_authenticate(chamber_admin)
    url = reverse_lazy("v1:super-admin:campaign-list")
    response = api_client.post(url, data=campaign_create_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_campaign_create_api_violate_restriction(
    super_admin: User,
    api_client: APIClient,
    campaign_create_data: dict,
):
    """Ensure that campaign name must be unique within chamber."""
    api_client.force_authenticate(super_admin)
    url = reverse_lazy("v1:super-admin:campaign-list")
    response = api_client.post(url, data=campaign_create_data)
    assert response.status_code == status.HTTP_201_CREATED
    response = api_client.post(url, data=campaign_create_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    expected_error_messages = {
        "Campaign with this name already exists.",
        "There is an ongoing campaign.",
    }
    response_error_messages = set(
        error["detail"] for error in response.data["errors"]
    )
    assert expected_error_messages == response_error_messages


# pylint: disable=too-many-arguments,unused-argument
def test_campaign_update_api(
    chamber_admin: User,
    completed_campaign: Campaign,
) -> None:
    """Ensure that chamber admin can update campaign."""
    chamber_admin.chamber = completed_campaign.chamber
    chamber_admin.save()
    new_campaign_year = completed_campaign.year + 1
    campaign_data = factory.build(
        dict,
        FACTORY_CLASS=CampaignFactory,
        chamber_id=completed_campaign.chamber_id,
        name=completed_campaign.name + ".",
        year=new_campaign_year,
        status=CampaignStatus.CREATED,
        start_date=date(new_campaign_year, 1, 1),
    )
    campaign_update_data = copy.deepcopy(campaign_data)
    campaign_update_data.pop("chamber")
    campaign = Campaign.objects.create(**campaign_data)
    campaign_update_data["status"] = CampaignStatus.LIVE
    campaign_update_data.update(
        {
            "year": new_campaign_year,
            "end_date": date(new_campaign_year, 12, 31),
            "report_close_weekday": 0,
            "report_close_time": "01:00",
        },
    )
    UserCampaignFactory(
        campaign_id=campaign.id,
        role=UserCampaignRole.CHAMBER_CHAIR,
    )
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(chamber_admin)
    url = reverse_lazy(
        "v1:chamber:campaign-detail",
        kwargs={"pk": campaign.pk},
    )
    response = api_client.put(url, data=campaign_update_data)
    assert response.status_code == status.HTTP_200_OK, response.data


def test_campaign_update_api_duplicated_name(
    chamber_admin: User,
    campaign: Campaign,
    chamber: Chamber,
    campaign_update_data: dict,
) -> None:
    """Ensure that campaign name must be unique within chamber."""
    another_campaign = CampaignFactory(
        chamber=chamber,
        status=CampaignStatus.CREATED,
    )
    campaign.status = CampaignStatus.CREATED
    campaign.save()
    chamber_admin.chamber = chamber
    chamber_admin.save()
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(chamber_admin)
    url = reverse_lazy(
        "v1:chamber:campaign-detail",
        kwargs={"pk": campaign.pk},
    )
    campaign_update_data["name"] = another_campaign.name
    response = api_client.put(
        url,
        data=campaign_update_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = api_client.put(
        url,
        data=campaign_update_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_live_campaign_update(
    chamber_admin: User,
    campaign: Campaign,
    chamber: Chamber,
    campaign_update_data: dict,
) -> None:
    """Ensure that campaign has status LIVE can only be updated to DONE."""
    campaign.status = CampaignStatus.LIVE
    campaign.save()
    chamber_admin.chamber = chamber
    chamber_admin.save()
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(chamber_admin)
    url = reverse_lazy(
        "v1:chamber:campaign-detail",
        kwargs={"pk": campaign.pk},
    )
    response = api_client.put(
        url,
        data=campaign_update_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_campaign_update_api_non_chamber_admin(
    campaign: Campaign,
) -> None:
    """Ensure that non-admin users cannot update campaign."""
    user = UserFactory()
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(user)
    url = reverse_lazy(
        "v1:chamber:campaign-detail",
        kwargs={"pk": campaign.pk},
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.skip(reason="Skip due to new logic")
def test_get_campaign_inventory_statistics_api(
    product_categories: list[ProductCategory],
    product: Product,
    levels: list[Level],
    chamber_admin_client: CAAPIClient,
) -> None:
    """Ensure CA can get campaign's inventory statistics from API."""
    _ = [LevelInstanceFactory(level=level) for level in levels]
    chamber_admin_client.select_campaign(product_categories[0].campaign)
    response = chamber_admin_client.get(
        reverse_lazy(
            "v1:chamber:campaign-get-inventory-stats",
        ),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["levels_count"] == len(levels)
    assert response.data["total_value"] == sum(level.cost for level in levels)


def test_get_landing_page_information(
    volunteer: User,
    api_client: APIClient,
) -> None:
    """Ensure that get landing page information API works as expected."""
    CampaignFactory(chamber=volunteer.chamber, status=CampaignStatus.LIVE)
    api_url = reverse_lazy(
        "v1:public:campaign-get-landing-page-information",
    ) + f"?chamber={volunteer.chamber_id}"
    response = api_client.get(api_url)
    assert response.status_code == status.HTTP_200_OK


def test_get_landing_page_information_campaign_not_in_progress(
    volunteer: User,
    api_client: APIClient,
) -> None:
    """Ensure that the API cannot be accessed when campaign not in progress."""
    CampaignFactory(chamber=volunteer.chamber, status=CampaignStatus.DONE)
    api_url = reverse_lazy(
        "v1:public:campaign-get-landing-page-information",
    ) + f"?chamber={volunteer.chamber_id}"
    response = api_client.get(api_url)
    assert response.status_code == status.HTTP_200_OK
