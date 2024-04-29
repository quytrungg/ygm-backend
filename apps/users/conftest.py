import pytest

from apps.users.constants import UserRole
from apps.users.factories import UserFactory
from apps.users.models import User


@pytest.fixture
def chamber_admin(chamber) -> User:
    """Create chamber admin user."""
    return UserFactory(role=UserRole.CHAMBER_ADMIN, chamber=chamber)
