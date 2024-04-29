"""Configuration file for pytest."""
import typing
from functools import partial

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.utils.module_loading import import_string

from rest_framework.test import APIClient

import pytest
import pytest_lazy_fixtures
from safedelete.config import HARD_DELETE

from apps.campaigns import factories as campaigns_factories
from apps.campaigns import models as campaigns_models
from apps.campaigns.constants import UserCampaignRole
from apps.chambers.factories import ChamberFactory
from apps.chambers.models import Chamber
from apps.core.test_utils import TestLevelData, create_volunteer
from apps.members import factories as members_factories
from apps.members import models as members_models
from apps.users.constants import UserRole
from apps.users.factories import UserFactory
from apps.users.models import User


def pytest_configure():
    """Set up Django settings for tests.

    `pytest` automatically calls this function once when tests are run.

    """
    pytest.lazy_fixture = pytest_lazy_fixtures.lf

    settings.DEBUG = False
    settings.RESTRICT_DEBUG_ACCESS = True
    settings.TESTING = True

    # The default password hasher is rather slow by design.
    # https://docs.djangoproject.com/en/dev/topics/testing/overview/
    settings.PASSWORD_HASHERS = (
        "django.contrib.auth.hashers.MD5PasswordHasher",
    )
    settings.EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    # To disable celery in tests
    settings.CELERY_TASK_ALWAYS_EAGER = True


@pytest.fixture(scope="session", autouse=True)
def django_db_setup(django_db_setup):
    """Set up test db for testing."""


@pytest.fixture(autouse=True)
# pylint: disable=invalid-name
def enable_db_access_for_all_tests(django_db_setup, db):
    """Enable access to DB for all tests."""


@pytest.fixture(scope="session", autouse=True)
def temp_directory_for_media(tmp_path_factory):
    """Fixture that set temp directory for all media files.

    This fixture changes default STORAGE to filesystem and provides temp dir
    for media. PyTest cleans up this temp dir by itself after few test runs.

    """
    settings.STORAGES["default"][
        "BACKEND"
    ] = "django.core.files.storage.FileSystemStorage"
    settings.MEDIA_ROOT = tmp_path_factory.mktemp("tmp_media")


@pytest.fixture(scope="session")
def super_admin(django_db_blocker) -> User:
    """Create a super admin user."""
    with django_db_blocker.unblock():
        admin = UserFactory(role=UserRole.SUPER_ADMIN)
        yield admin
        admin.delete()


@pytest.fixture(scope="session")
def chamber_admin(django_db_blocker) -> User:
    """Create chamber admin user."""
    with django_db_blocker.unblock():
        user = UserFactory(role=UserRole.CHAMBER_ADMIN)
        yield user
        user.delete(force_policy=HARD_DELETE)


@pytest.fixture(scope="session")
def volunteer(django_db_blocker) -> User:
    """Create volunteer user."""
    with django_db_blocker.unblock():
        user = UserFactory(role=UserRole.VOLUNTEER)
        yield user
        user.delete(force_policy=HARD_DELETE)


@pytest.fixture(scope="session")
def super_admin_client(super_admin: User) -> APIClient:
    """Create api client for super admin."""
    client = APIClient()
    client.force_authenticate(super_admin)
    return client


@pytest.fixture(scope="session")
def chamber_admin_client(chamber_admin: User) -> APIClient:
    """Create api client for chamber admin."""
    client = APIClient()
    client.force_authenticate(chamber_admin)
    return client


@pytest.fixture
def create_file():
    """Return a function to create uploaded file."""

    def _create_file(filename: str):
        """Return the uploaded file's url path."""
        test_file = SimpleUploadedFile(
            filename,
            b"test",
            content_type="image/png",
        )
        file_storage_cls = import_string(
            settings.STORAGES["default"]["BACKEND"],
        )
        file_storage = file_storage_cls()
        file = file_storage.save(filename, test_file)
        return file_storage.url(file)

    return _create_file


@pytest.fixture
def chamber() -> Chamber:
    """Return a chamber."""
    return ChamberFactory()


@pytest.fixture(scope="session")
def setup_product() -> typing.Callable:
    """Return a function to set up product's levels."""

    def _setup(
        product: campaigns_models.Product,
        levels_data: list[TestLevelData],
    ) -> list[campaigns_models.Level]:
        """Set up levels for a product."""
        _volunteer = create_volunteer(
            product.category.campaign,
            role=UserCampaignRole.VOLUNTEER,
        )
        new_approved_contract = partial(
            members_factories.ContractFactory,
            created_by=_volunteer,
            status=members_models.Contract.STATUSES.APPROVED,
        )
        levels = []
        for level_data in levels_data:
            contract_credits = []
            level = campaigns_factories.LevelFactory(
                **level_data.level_info,
                product=product,
            )
            levels.append(level)
            sold_instances = [
                campaigns_models.LevelInstance(
                    level=level,
                    cost=level.cost,
                    contract=new_approved_contract(
                        campaign=level.product.category.campaign,
                    ),
                )
                for _ in range(level_data.sold_count)
            ]
            declined_count = level_data.declined_count
            declined_instances = [
                campaigns_models.LevelInstance(
                    level=level,
                    cost=level.cost,
                    declined_at=timezone.now(),
                    contract=new_approved_contract(
                        campaign=level.product.category.campaign,
                    ),
                )
                for _ in range(declined_count)
            ]
            available_count = level_data.total_count - level_data.sold_count
            available_instances = [
                campaigns_models.LevelInstance(
                    level=level,
                    cost=level.cost,
                    contract=None,
                )
                for _ in range(available_count)
            ]
            campaigns_models.LevelInstance.objects.bulk_create(
                sold_instances + available_instances + declined_instances,
            )
            contract_credits = [
                members_models.ContractCreditInfo(
                    user_campaign=level_instance.contract.created_by,
                    contract=level_instance.contract,
                    portion=1,
                )
                for level_instance in sold_instances + declined_instances
            ]
            members_models.ContractCreditInfo.objects.bulk_create(
                contract_credits,
            )
        return levels

    return _setup
