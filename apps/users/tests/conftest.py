import typing

from rest_framework import test

import pytest

from .. import factories, models


@pytest.fixture(scope="module")
def user(django_db_blocker) -> typing.Generator[models.User, None, None]:
    """Module-level fixture for user."""
    with django_db_blocker.unblock():
        created_user = factories.UserFactory()
        yield created_user
        created_user.delete()


@pytest.fixture
def user_api_client(
    api_client: test.APIClient,
    user: models.User,
) -> test.APIClient:
    """Create api client."""
    api_client.force_authenticate(user)
    return api_client
