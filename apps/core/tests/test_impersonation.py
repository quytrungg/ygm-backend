from django.urls import reverse

from rest_framework.test import APIClient

import pytest
from knox.models import AuthToken

from apps.chambers import factories as chamber_factories
from apps.chambers import models as chamber_models
from apps.users import factories as user_factories
from apps.users import models as user_models
from apps.users.constants import UserRole


@pytest.fixture
def chamber(django_db_blocker) -> chamber_models.Chamber:
    """Return a chamber."""
    with django_db_blocker.unblock():
        _chamber = chamber_factories.ChamberFactory()
        yield _chamber
        _chamber.hard_delete()


@pytest.fixture
def another_chamber_id(django_db_blocker) -> int:
    """Return another chamber's id."""
    with django_db_blocker.unblock():
        _chamber = chamber_factories.ChamberFactory()
        yield _chamber.id
        _chamber.hard_delete()


@pytest.fixture
def super_admin(django_db_blocker) -> user_models.User:
    """Return a super admin user."""
    with django_db_blocker.unblock():
        admin = user_factories.UserFactory(role=UserRole.SUPER_ADMIN)
        yield admin
        admin.hard_delete()


@pytest.fixture
def chamber_admin(
    django_db_blocker,
    chamber: chamber_models.Chamber,
) -> user_models.User:
    """Return a chamber admin user."""
    with django_db_blocker.unblock():
        admin = user_factories.UserFactory(
            role=UserRole.CHAMBER_ADMIN,
            chamber_id=chamber.id,
        )
        yield admin
        admin.hard_delete()


@pytest.fixture
def chamber_admin_token(
    django_db_blocker,
    chamber_admin: user_models.User,
) -> str:
    """Return auth token for chamber admin."""
    with django_db_blocker.unblock():
        instance, token = AuthToken.objects.create(chamber_admin)
        yield token
        instance.delete()


@pytest.fixture
def super_admin_token(
    django_db_blocker,
    super_admin: user_models.User,
) -> str:
    """Return auth token for super admin."""
    with django_db_blocker.unblock():
        instance, token = AuthToken.objects.create(super_admin)
        yield token
        instance.delete()


def test_super_admin_impersonation(
    super_admin_token: str,
    super_admin: user_models.User,
    chamber_admin: user_models.User,
):
    """Ensure super admin can impersonate as chamber admin.

    Assert that when impersonate header is valid, returned user is chamber
    admin, while returned auth token instance belongs to original super admin.

    """
    client = APIClient()
    request_headers = {
        "authorization": f"Token {super_admin_token}",
        "chamber": chamber_admin.chamber_id,
    }
    response = client.get(
        reverse("impersonate-info"),
        headers=request_headers,
    )
    assert response.data["user_id"] == chamber_admin.id
    assert response.data["auth_user_id"] == super_admin.id


def test_super_admin_impersonation_fail(
    super_admin_token: str,
    super_admin: user_models.User,
    chamber_admin: user_models.User,
):
    """Ensure super admin can't impersonate if chamber id is not valid."""
    client = APIClient()
    request_headers = {
        "authorization": f"Token {super_admin_token}",
        "chamber": "abcd",
    }
    response = client.get(
        reverse("impersonate-info"),
        headers=request_headers,
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    argnames="chamber_header",
    argvalues=[
        {"chamber": ""},
        {},
    ],
)
def test_super_admin_no_impersonation(
    super_admin_token: str,
    super_admin: user_models.User,
    chamber_header: dict,
):
    """Ensure authentication class returns super admin if no impersonation.

    If impersonate header is not present or invalid, no impersonation happens.

    """
    client = APIClient()
    request_headers = {
        "authorization": f"Token {super_admin_token}",
    }
    request_headers.update(chamber_header)
    response = client.get(
        reverse("impersonate-info"),
        headers=request_headers,
    )
    assert response.status_code == 200, response.data
    assert response.data["user_id"] == super_admin.id
    assert response.data["auth_user_id"] == super_admin.id


@pytest.mark.parametrize(
    argnames=["user", "auth_token"],
    argvalues=[
        [
            pytest.lazy_fixture("chamber_admin"),
            pytest.lazy_fixture("chamber_admin_token"),
        ],
    ],
)
@pytest.mark.parametrize(
    argnames="chamber_header",
    argvalues=[
        {"chamber": ""},
        {"chamber": pytest.lazy_fixture("another_chamber_id")},
    ],
)
def test_non_super_admin_impersonation(
    user: user_models.User,
    auth_token: str,
    chamber_header: dict,
):
    """Ensure non SA user can't impersonate in any case."""
    client = APIClient()
    request_headers = {
        "authorization": f"Token {auth_token}",
    }
    request_headers.update(chamber_header)
    response = client.get(
        reverse("impersonate-info"),
        headers=request_headers,
    )
    assert response.status_code == 200, response.data
    assert response.data["user_id"] == user.id
    assert response.data["auth_user_id"] == user.id
