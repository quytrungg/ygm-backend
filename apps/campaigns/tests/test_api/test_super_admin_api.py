from datetime import date, timedelta

from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.test import APIClient

from apps.campaigns.models import Campaign
from apps.users.factories import UserFactory
from apps.users.models import User


def test_campaign_list_api(super_admin: User, api_client: APIClient) -> None:
    """Ensure that super admin user can access to campaign list API."""
    api_client.force_authenticate(super_admin)
    url = reverse_lazy("v1:super-admin:campaign-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_campaign_list_api_non_super_admin(api_client: APIClient) -> None:
    """Ensure that non super admin user cannot access to campaign list API."""
    user = UserFactory()
    api_client.force_authenticate(user)
    url = reverse_lazy("v1:super-admin:campaign-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_campaign_create_api(
    super_admin: User,
    api_client: APIClient,
    campaign_create_data: dict,
) -> None:
    """Ensure super admin can create campaign."""
    api_client.force_authenticate(super_admin)
    url = reverse_lazy("v1:super-admin:campaign-list")
    response = api_client.post(url, data=campaign_create_data)
    assert response.status_code == status.HTTP_201_CREATED


def test_campaign_update_api(
    super_admin: User,
    api_client: APIClient,
    campaign: Campaign,
    campaign_update_data: dict,
) -> None:
    """Ensure super admin can update campaign."""
    api_client.force_authenticate(super_admin)
    url = reverse_lazy(
        "v1:super-admin:campaign-detail",
        kwargs={"pk": campaign.pk},
    )
    campaign_update_data["end_date"] = date.today() + timedelta(days=1)
    campaign_update_data["timezone"] = str(campaign.timezone)
    response = api_client.put(url, data=campaign_update_data)
    assert response.status_code == status.HTTP_200_OK, response.data


def test_campaign_update_api_non_admin_user(
    api_client: APIClient,
    campaign: Campaign,
) -> None:
    """Ensure non admin user cannot update campaign."""
    user = UserFactory()
    api_client.force_authenticate(user)
    url = reverse_lazy(
        "v1:super-admin:campaign-detail",
        kwargs={"pk": campaign.pk},
    )
    response = api_client.put(url, data={"name": "New name"})
    assert response.status_code == status.HTTP_403_FORBIDDEN
