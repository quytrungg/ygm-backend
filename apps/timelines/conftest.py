import datetime as dt
import typing

from rest_framework.test import APIClient

import pytest
from safedelete.config import HARD_DELETE

from apps.chambers.factories import ChamberFactory
from apps.chambers.models import Chamber
from apps.core.test_utils import get_test_file_url
from apps.users.constants import UserRole
from apps.users.factories import UserFactory
from apps.users.models import User

from .constants import TimelineStatus
from .factories import TimelineCategoryFactory, TimelineFactory
from .models import Timeline, TimelineCategory


@pytest.fixture
def chamber(django_db_blocker) -> Chamber:
    """Return a chamber."""
    with django_db_blocker.unblock():
        chamber_instance = ChamberFactory()
        yield chamber_instance
        chamber_instance.delete(force_policy=HARD_DELETE)


@pytest.fixture
def another_chamber(django_db_blocker) -> ChamberFactory:
    """Return another chamber instance."""
    with django_db_blocker.unblock():
        chamber_instance = ChamberFactory()
        yield chamber_instance
        chamber_instance.delete(force_policy=HARD_DELETE)


@pytest.fixture
def chamber_admin(django_db_blocker, chamber: Chamber) -> User:
    """Create chamber admin user."""
    with django_db_blocker.unblock():
        user = UserFactory(
            role=UserRole.CHAMBER_ADMIN,
            chamber=chamber,
        )
        yield user
        user.delete(force_policy=HARD_DELETE)


@pytest.fixture
def chamber_admin_client(chamber_admin: User) -> APIClient:
    """Create api client for chamber admin."""
    client = APIClient()
    client.force_authenticate(chamber_admin)
    return client


@pytest.fixture
def timeline_category() -> TimelineCategory:
    """Create a timeline category."""
    return TimelineCategoryFactory()


@pytest.fixture
def timeline(chamber: Chamber) -> Timeline:
    """Return a timeline."""
    return TimelineFactory(chamber=chamber, status=TimelineStatus.IN_PROGRESS)


@pytest.fixture
def another_timeline(
    chamber_admin: User,
    another_chamber: Chamber,
) -> Timeline:
    """Return another timeline instance."""
    return TimelineFactory(
        assigned_to=chamber_admin,
        chamber=another_chamber,
    )


@pytest.fixture
def timeline_create_data(
    timeline_category: TimelineCategory,
    create_file: typing.Callable,
) -> dict:
    """Return data to create timeline objects."""
    return {
        "name": "Test Timeline",
        "description": "Timeline Description",
        "due_date": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": TimelineStatus.NOT_STARTED.value,
        "category": timeline_category.pk,
        "assigned_to": "A Role",
        "attachments": [
            {
                "name": "test.png",
                "file": get_test_file_url(create_file("test.png")),
                "content_type": "img/png",
            },
            {
                "name": "notes.txt",
                "file": get_test_file_url(create_file("notes.txt")),
                "content_type": "txt",
            },
        ],
    }


@pytest.fixture
def timeline_update_data(
    timeline_create_data: dict,
    create_file: typing.Callable,
) -> dict:
    """Return timeline updated data."""
    return {
        **timeline_create_data,
        "attachments": [
            {
                "name": "updated.png",
                "file": get_test_file_url(create_file("updated.png")),
                "content_type": "img/png",
            },
        ],
    }
