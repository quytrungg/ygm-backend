from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.test import APIClient

import pytest

from apps.chambers.factories import ChamberBrandingFactory
from apps.chambers.models import Chamber, ChamberBranding
from apps.core.test_utils import get_test_file_url
from apps.users.factories import UserFactory
from apps.users.models import User


@pytest.fixture
def chamber_branding(chamber: Chamber) -> ChamberBranding:
    """Return a chamber branding."""
    return ChamberBrandingFactory(chamber=chamber)


@pytest.fixture
def chamber_branding_update_date(create_file) -> dict:
    """Return data for updating chamber branding."""
    return {
        "site_primary_color": "#282B30",
        "site_secondary_color": "#282B30",
        "site_alternate_color": "#282B30",
        "chamber_logo": get_test_file_url(create_file("avatar.png")),
        "trc_logo": get_test_file_url(create_file("avatar.png")),
        "landing_bg": get_test_file_url(create_file("avatar.png")),
        "headline": "Headline",
    }


@pytest.fixture
def chamber_branding_messages_update_data(chamber_branding: Chamber) -> dict:
    """Return updated data for chamber branding prelaunch messages."""
    return {
        "public_prelaunch_msg": chamber_branding.public_prelaunch_msg,
        "volunteer_prelaunch_msg": chamber_branding.volunteer_prelaunch_msg,
    }


def test_chamber_branding_detail_api(
    api_client: APIClient,
    chamber_admin: User,
    chamber: Chamber,
    chamber_branding: ChamberBranding,
) -> None:
    """Ensure that chamber branding detail API works for chamber admin."""
    chamber_admin.chamber = chamber
    chamber_admin.save()
    api_client.force_authenticate(user=chamber_admin)
    url = reverse_lazy("v1:chamber:branding")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_chamber_branding_detail_api_non_admin_user(
    api_client: APIClient,
) -> None:
    """Ensure that non-admin user cannot access chamber branding detail API."""
    api_client.force_authenticate(user=UserFactory())
    url = reverse_lazy("v1:chamber:branding")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_chamber_branding_update_api(
    api_client: APIClient,
    chamber_admin: User,
    chamber: Chamber,
    chamber_branding: ChamberBranding,
    chamber_branding_update_date: dict,
) -> None:
    """Ensure that chamber branding update API works for chamber admin."""
    chamber_admin.chamber = chamber
    chamber_admin.save()
    api_client.force_authenticate(user=chamber_admin)
    url = reverse_lazy("v1:chamber:branding")
    response = api_client.put(url, chamber_branding_update_date)
    assert response.status_code == status.HTTP_200_OK


def test_chamber_branding_update_api_non_admin_user(
    api_client: APIClient,
    chamber_branding_update_date: dict,
) -> None:
    """Ensure that non-admin user cannot access chamber branding update API."""
    api_client.force_authenticate(user=UserFactory())
    url = reverse_lazy("v1:chamber:branding")
    response = api_client.put(url, chamber_branding_update_date)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_chamber_branding_update_messages_api(
    api_client: APIClient,
    chamber_admin: User,
    chamber: Chamber,
    chamber_branding_messages_update_data: dict,
) -> None:
    """Ensure CA can update chamber branding public and volunteer messages."""
    chamber_admin.chamber = chamber
    chamber_admin.save()
    api_client.force_authenticate(user=chamber_admin)
    response = api_client.patch(
        reverse_lazy("v1:chamber:branding"),
        data=chamber_branding_messages_update_data,
    )
    assert response.status_code == status.HTTP_200_OK, response.data
