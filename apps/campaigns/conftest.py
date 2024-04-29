from rest_framework.test import APIClient

import pytest
from safedelete.config import HARD_DELETE

from apps.campaigns import constants as campaign_constants
from apps.campaigns import factories as campaign_factories
from apps.campaigns.constants import CampaignStatus, UserCampaignRole
from apps.campaigns.factories import (
    CampaignFactory,
    LevelFactory,
    LevelInstanceFactory,
    ProductCategoryFactory,
    ProductFactory,
    TeamFactory,
    UserCampaignFactory,
)
from apps.campaigns.models import (
    Campaign,
    Level,
    LevelInstance,
    Product,
    ProductCategory,
    Team,
    UserCampaign,
)
from apps.chambers import factories as chamber_factories
from apps.chambers.factories import ChamberFactory
from apps.chambers.models import Chamber
from apps.core.test_utils import CAAPIClient
from apps.members.constants import ContractStatus
from apps.members.factories import ContractFactory, MemberFactory
from apps.members.models import Contract, Member
from apps.timelines.constants import TimelineTypeChoice
from apps.timelines.models import TimelineType
from apps.users import factories
from apps.users.constants import UserRole
from apps.users.factories import UserFactory
from apps.users.models import User


@pytest.fixture
def campaign(chamber: Chamber) -> Campaign:
    """Return a campaign."""
    _campaign = CampaignFactory(chamber=chamber, status=CampaignStatus.CREATED)
    yield _campaign
    _campaign.delete(force_policy=HARD_DELETE)


@pytest.fixture
def campaign_create_data(chamber: Chamber) -> dict:
    """Return data for creating campaign."""
    return {
        "name": "Campaign name",
        "year": 2024,
        "timeline_id": TimelineType.objects.get(name=TimelineTypeChoice.WITH_VICE_CHAIR).id,  # noqa: E501 # pylint: disable=line-too-long
        "goal": 1000,
        "chamber": chamber.pk,
    }


@pytest.fixture
def chamber(django_db_blocker):
    """Return a test Chamber."""
    with django_db_blocker.unblock():
        _chamber = ChamberFactory()
        yield _chamber
        _chamber.hard_delete()


@pytest.fixture
def another_chamber(django_db_blocker) -> Chamber:
    """Return another test Chamber."""
    with django_db_blocker.unblock():
        _chamber = ChamberFactory()
        yield _chamber
        _chamber.hard_delete()


@pytest.fixture
def open_campaign(chamber: Chamber, django_db_blocker) -> Campaign:
    """Return an open campaign of `chamber`."""
    with django_db_blocker.unblock():
        _campaign = CampaignFactory(
            chamber=chamber,
            status=CampaignStatus.CREATED,
        )
        yield _campaign
        _campaign.hard_delete()


@pytest.fixture
def active_campaign(
    open_campaign: Campaign,
    django_db_blocker,
) -> Campaign:
    """Return an `active` campaign."""
    with django_db_blocker.unblock():
        open_campaign.status = CampaignStatus.LIVE
        open_campaign.save()
        yield open_campaign
        open_campaign.status = CampaignStatus.CREATED
        open_campaign.save()


@pytest.fixture
def completed_campaign(
    open_campaign: Campaign,
    django_db_blocker,
) -> Campaign:
    """Return a `completed` campaign."""
    with django_db_blocker.unblock():
        open_campaign.status = CampaignStatus.DONE
        open_campaign.save()
        yield open_campaign
        open_campaign.status = CampaignStatus.CREATED
        open_campaign.save()


@pytest.fixture
def chamber_admin(chamber: Chamber, django_db_blocker) -> User:
    """Return admin of `chamber`."""
    with django_db_blocker.unblock():
        _chamber_admin = UserFactory(
            chamber=chamber,
            role=UserRole.CHAMBER_ADMIN,
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
def another_chamber_admin_client(another_chamber: Chamber) -> CAAPIClient:
    """Return client of another chamber."""
    user = UserFactory(chamber=another_chamber, role=UserRole.CHAMBER_ADMIN)
    client = CAAPIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def volunteer(chamber: Chamber) -> User:
    """Create a volunteer."""
    return UserFactory(role=UserRole.VOLUNTEER, chamber=chamber)


@pytest.fixture
def volunteer_client(volunteer: User) -> APIClient:
    """Return an API client logged in as volunteer."""
    client = APIClient()
    client.force_authenticate(volunteer)
    return client


@pytest.fixture
def team(open_campaign: Campaign) -> Team:
    """Return a test team instance."""
    return TeamFactory(campaign=open_campaign)


@pytest.fixture
def another_team(open_campaign: Campaign) -> Team:
    """Return another test team instance."""
    return TeamFactory(campaign=open_campaign)


@pytest.fixture
def teams(open_campaign: Campaign) -> list[Team]:
    """Return batch of team instances for testing."""
    return TeamFactory.create_batch(size=3, campaign=open_campaign)


@pytest.fixture
def team_captain_team_1(open_campaign: Campaign, team: Team) -> UserCampaign:
    """Return a team captain with `team` fixture (team 1)."""
    return UserCampaignFactory(
        team=team,
        role=UserCampaignRole.TEAM_CAPTAIN,
        campaign=open_campaign,
    )


@pytest.fixture
def team_captain_team_2(
    open_campaign: Campaign,
    another_team: Team,
) -> UserCampaign:
    """Return a team captain with `another_team` fixture (team 2)."""
    return UserCampaignFactory(
        team=another_team,
        role=UserCampaignRole.TEAM_CAPTAIN,
        campaign=open_campaign,
    )


@pytest.fixture
def volunteers_team_1(
    open_campaign: Campaign,
    team: Team,
) -> list[UserCampaign]:
    """Return list of volunteers with `team` fixture (team 1)."""
    return UserCampaignFactory.create_batch(
        size=3,
        team=team,
        role=UserCampaignRole.VOLUNTEER,
        campaign=open_campaign,
    )


@pytest.fixture
def team_captains_team_1(
    open_campaign: Campaign,
    team: Team,
) -> list[UserCampaign]:
    """Return members in team 1 with a team captain."""
    return UserCampaignFactory.create_batch(
        size=3,
        team=team,
        role=UserCampaignRole.TEAM_CAPTAIN,
        campaign=open_campaign,
    )


@pytest.fixture
def chamber_chair_users(open_campaign: Campaign) -> list[UserCampaign]:
    """Return list of chamber chair users."""
    return UserCampaignFactory.create_batch(
        size=3,
        role=UserCampaignRole.CHAMBER_CHAIR,
        campaign=open_campaign,
    )


@pytest.fixture
def chamber_admin_2(django_db_blocker) -> User:
    """Return a chamber admin."""
    with django_db_blocker.unblock():
        _chamber = chamber_factories.ChamberFactory()
        _chamber_admin = factories.UserFactory(
            role=UserRole.CHAMBER_ADMIN,
            chamber=_chamber,
            email=_chamber.trc_coord_email,
        )
        _ = campaign_factories.CampaignFactory(
            name="Summer Camp",
            status=campaign_constants.CampaignStatus.CREATED,
            chamber=_chamber,
        )
        yield _chamber_admin
        _chamber_admin.delete(force_policy=HARD_DELETE)
        _chamber.delete(force_policy=HARD_DELETE)


@pytest.fixture
def another_chamber_admin(django_db_blocker) -> User:
    """Return a chamber admin of another chamber."""
    with django_db_blocker.unblock():
        _chamber = chamber_factories.ChamberFactory()
        _chamber_admin = factories.UserFactory(
            role=UserRole.CHAMBER_ADMIN,
            chamber=_chamber,
            email=_chamber.trc_coord_email,
        )
        _ = campaign_factories.CampaignFactory(
            status=campaign_constants.CampaignStatus.CREATED,
            chamber=_chamber,
        )
        return _chamber_admin


@pytest.fixture
def signed_contract(active_campaign: Campaign) -> Contract:
    """Return a contract."""
    return ContractFactory(
        status=ContractStatus.SIGNED,
        campaign=active_campaign,
    )


@pytest.fixture
def product_category(open_campaign: Campaign) -> ProductCategory:
    """Return a test product category."""
    return ProductCategoryFactory(campaign=open_campaign)


@pytest.fixture
def product_categories(campaign: Campaign) -> list[ProductCategory]:
    """Return list of product categories for testing."""
    return ProductCategoryFactory.create_batch(3, campaign=campaign)


@pytest.fixture
def product(product_category: ProductCategory) -> Product:
    """Return a test product."""
    return ProductFactory(category=product_category)


@pytest.fixture
def levels(product: Product) -> list[Level]:
    """Return a list of levels for testing."""
    return LevelFactory.create_batch(size=3, product=product)


@pytest.fixture
def level(product: Product) -> Level:
    """Return a test level."""
    return LevelFactory(product=product)


@pytest.fixture
def level_instance(signed_contract: Contract, level: Level) -> LevelInstance:
    """Return a test level instance."""
    return LevelInstanceFactory(
        contract=signed_contract,
        level=level,
        declined_at=None,
    )


@pytest.fixture
def level_instance_no_contract(level: Level) -> LevelInstance:
    """Return a level instance without any contract."""
    return LevelInstanceFactory(contract=None, declined_at=None, level=level)


@pytest.fixture
def level_instances(
    signed_contract: Contract,
    level: Level,
) -> list[LevelInstance]:
    """Return batch of 5 level instances."""
    return LevelInstanceFactory.create_batch(
        size=5,
        contract=signed_contract,
        level=level,
        declined_at=None,
    )


@pytest.fixture
def campaign_update_data() -> dict:
    """Return data for updating campaign."""
    return {
        "name": "New name",
        "timeline_id": TimelineType.objects.get(name=TimelineTypeChoice.WITHOUT_VICE_CHAIR).id,  # noqa: E501 # pylint: disable=line-too-long
        "status": CampaignStatus.CREATED,
        "goal": 1000,
        "report_close_weekday": 0,
        "report_close_time": "09:00",
        "has_vice_chairs": True,
        "has_trades": True,
    }


@pytest.fixture
def members() -> Member:
    """Create a batch of members."""
    return MemberFactory.create_batch(size=3)
