from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

import pytest

from apps.core.test_utils import get_test_file_url
from apps.users.factories import UserFactory
from apps.users.models import User


@pytest.fixture
def profile_update_data(create_file) -> dict:
    """Return data for updating profile."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "avatar": get_test_file_url(create_file("avatar.png")),
        "preference": {
            "favorite_candy": "Chocolate",
            "favorite_drink": "Coffee",
            "favorite_restaurant": "McDonald's",
            "favorite_movie": "The Matrix",
            "hobbies": "Coding",
        },
    }


def test_profile_update_api_super_admin(
    super_admin: User,
    api_client: APIClient,
    profile_update_data: dict,
) -> None:
    """Ensure that super admin can update their profile."""
    api_client.force_authenticate(user=super_admin)
    url = reverse("v1:super-admin:profile")
    response = api_client.put(url, profile_update_data)
    assert response.status_code == status.HTTP_200_OK


def test_profile_update_api_chamber_admin(
    chamber_admin: User,
    api_client: APIClient,
    profile_update_data: dict,
) -> None:
    """Ensure that chamber admin can update their profile."""
    api_client.force_authenticate(user=chamber_admin)
    url = reverse("v1:chamber:profile")
    response = api_client.put(url, profile_update_data)
    assert response.status_code == status.HTTP_200_OK


def test_profile_update_api_non_super_admin_user(
    api_client: APIClient,
    profile_update_data: dict,
) -> None:
    """Ensure that non admin user can't access the admin profile update API."""
    api_client.force_authenticate(user=UserFactory())
    url = reverse("v1:super-admin:profile")
    response = api_client.put(url, profile_update_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_profile_update_non_admin_user(
    api_client: APIClient,
    profile_update_data: dict,
) -> None:
    """Ensure that non admin user can't access the admin profile update API."""
    api_client.force_authenticate(user=UserFactory())
    url = reverse("v1:chamber:profile")
    response = api_client.put(url, profile_update_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
