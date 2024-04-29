import typing
from decimal import Decimal

from django.utils import timezone

from rest_framework.test import APIClient

import pytest

from apps.campaigns import factories as cmp_factories
from apps.campaigns import models as cmp_models
from apps.campaigns.constants import CampaignStatus, UserCampaignRole
from apps.chambers.factories import ChamberFactory
from apps.chambers.models import Chamber
from apps.core.test_utils import CAAPIClient
from apps.members import factories as mbr_factories
from apps.members import models as mbr_models
from apps.members.constants import ContractStatus
from apps.users.factories import UserFactory
from apps.users.models import User


class ContractLevelData(typing.TypedDict):
    """Represent simple data to set up a contract's level."""

    cost: Decimal
    is_declined: bool


@pytest.fixture
def setup_contract(
    campaign: cmp_models.Campaign,
    member: mbr_models.Member,
) -> typing.Callable:
    """Return factory function to set up contract's data."""
    def _setup(
        level_data: typing.Iterable[ContractLevelData],
    ) -> mbr_models.Contract:
        """Set up contract's data."""
        _contract = mbr_factories.ContractFactory(
            campaign=campaign,
            member=member,
        )
        category = cmp_factories.ProductCategoryFactory(
            campaign=campaign,
        )
        product = cmp_factories.ProductFactory(category=category)
        for data in level_data:
            _level = cmp_factories.LevelFactory(
                product=product,
                cost=data["cost"],
            )
            declined_at = timezone.now() if data["is_declined"] else None
            _ = cmp_models.LevelInstance.objects.create(
                level=_level,
                cost=_level.cost,
                declined_at=declined_at,
                contract=_contract,
            )
        return _contract
    return _setup


@pytest.fixture
def chamber(django_db_blocker) -> Chamber:
    """Return a test Chamber."""
    with django_db_blocker.unblock():
        _chamber = ChamberFactory()
        yield _chamber
        _chamber.hard_delete()


@pytest.fixture
def chamber_admin(chamber: Chamber, django_db_blocker) -> User:
    """Return admin of `chamber`."""
    with django_db_blocker.unblock():
        _chamber_admin = UserFactory(
            chamber=chamber,
            role=User.ROLES.CHAMBER_ADMIN,
        )
        yield _chamber_admin
        _chamber_admin.hard_delete()


@pytest.fixture
def chamber_admin_client(chamber_admin: User) -> CAAPIClient:
    """Return an API client logged in as `chamber_admin`."""
    client = CAAPIClient()
    client.force_authenticate(chamber_admin)
    return client


@pytest.fixture
def open_campaign(chamber: Chamber, django_db_blocker) -> cmp_models.Campaign:
    """Return an open campaign of `chamber`."""
    with django_db_blocker.unblock():
        _campaign = cmp_factories.CampaignFactory(
            chamber=chamber,
            status=CampaignStatus.CREATED,
        )
        yield _campaign
        _campaign.hard_delete()


@pytest.fixture
def active_campaign(
    chamber: Chamber,
    django_db_blocker,
) -> cmp_models.Campaign:
    """Return a live campaign of `chamber`."""
    with django_db_blocker.unblock():
        _campaign = cmp_factories.CampaignFactory(
            chamber=chamber,
            status=CampaignStatus.LIVE,
        )
        yield _campaign
        _campaign.hard_delete()


@pytest.fixture
def completed_campaign(
    chamber: Chamber,
    django_db_blocker,
) -> cmp_models.Campaign:
    """Return a completed campaign of `chamber`."""
    with django_db_blocker.unblock():
        _campaign = cmp_factories.CampaignFactory(
            chamber=chamber,
            status=CampaignStatus.DONE,
        )
        yield _campaign
        _campaign.hard_delete()


@pytest.fixture
def draft_contract(
    active_campaign: cmp_models.Campaign,
) -> mbr_models.Contract:
    """Return a draft contract instance."""
    return mbr_factories.ContractFactory(
        status=ContractStatus.DRAFT,
        campaign=active_campaign,
    )


@pytest.fixture
def approved_contract(
    active_campaign: cmp_models.Campaign,
) -> mbr_models.Contract:
    """Return an approved contract instance."""
    return mbr_factories.ContractFactory(
        status=ContractStatus.APPROVED,
        campaign=active_campaign,
    )


@pytest.fixture
def contracts(
    active_campaign: cmp_models.Campaign,
) -> list[mbr_models.Contract]:
    """Return batch of 10 contracts."""
    return mbr_factories.ContractFactory.create_batch(
        size=10,
        campaign=active_campaign,
    )


@pytest.fixture
def campaign(chamber) -> cmp_models.Campaign:
    """Return an open campaign within the chamber."""
    return cmp_factories.CampaignFactory(
        chamber=chamber,
        status=CampaignStatus.CREATED,
    )


@pytest.fixture
def member() -> mbr_models.Member:
    """Return a member."""
    return mbr_factories.MemberFactory()


@pytest.fixture
def members() -> list[mbr_models.Member]:
    """Return a batch of members."""
    return mbr_factories.MemberFactory.create_batch(size=3)


@pytest.fixture
def invoice() -> mbr_models.Invoice:
    """Return an invoice."""
    return mbr_factories.InvoiceFactory()


@pytest.fixture
def contract(
    user_campaign: cmp_models.UserCampaign,
    member: mbr_models.Member,
    active_campaign: cmp_models.Campaign,
) -> mbr_models.Contract:
    """Return a contract."""
    return mbr_factories.ContractFactory(
        member=member,
        campaign=active_campaign,
        created_by=user_campaign,
        status=mbr_models.Contract.STATUSES.DRAFT,
    )


@pytest.fixture
def level() -> cmp_models.Level:
    """Create a level instance."""
    return cmp_factories.LevelFactory()


@pytest.fixture
def level_instances_with_contract(
    level: cmp_models.Level,
    contract: mbr_models.Contract,
) -> list[cmp_models.LevelInstance]:
    """Create a batch of level instances attached to contract."""
    return cmp_factories.LevelInstanceFactory.create_batch(
        size=2,
        level=level,
        contract=contract,
    )


@pytest.fixture
def level_instances_without_contract(
    level: cmp_models.Level,
) -> list[cmp_models.LevelInstance]:
    """Create a batch of level instances without attachment to any contract."""
    return cmp_factories.LevelInstanceFactory.create_batch(
        size=2,
        level=level,
        contract=None,
    )


@pytest.fixture
def volunteer(chamber: Chamber) -> User:
    """Create a volunteer with chamber."""
    return UserFactory(role=User.ROLES.VOLUNTEER, chamber=chamber)


@pytest.fixture
def user_campaign(active_campaign: cmp_models.Campaign, volunteer: User):
    """Create a user campaign."""
    return cmp_factories.UserCampaignFactory(
        campaign=active_campaign,
        user=volunteer,
        role=UserCampaignRole.VOLUNTEER,
    )


@pytest.fixture
def volunteer_client(volunteer: User) -> APIClient:
    """Create api client login as volunteer."""
    client = APIClient()
    client.force_authenticate(volunteer)
    return client


@pytest.fixture
def another_volunteer(chamber: Chamber) -> User:
    """Create another volunteer with chamber."""
    return UserFactory(role=User.ROLES.VOLUNTEER, chamber=chamber)


@pytest.fixture
def another_volunteer_client(another_volunteer: User) -> APIClient:
    """Create api client login as `another_volunteer`."""
    client = APIClient()
    client.force_authenticate(another_volunteer)
    return client
