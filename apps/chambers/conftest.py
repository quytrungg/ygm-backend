import pytest
from safedelete.config import HARD_DELETE

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
    Product,
    ProductCategory,
    UserCampaign,
)
from apps.chambers.factories import ChamberFactory
from apps.chambers.models import Chamber
from apps.incentives.factories import (
    IncentiveFactory,
    IncentiveQualifierFactory,
)
from apps.members.factories import ContractFactory
from apps.members.models import Contract


@pytest.fixture(scope="module")
def chambers() -> list[Chamber]:
    """Return a list of Chambers."""
    created_chambers = ChamberFactory.create_batch(size=3)
    yield created_chambers
    Chamber.objects.filter(
        id__in=[chamber.id for chamber in created_chambers],
    ).delete(force_policy=HARD_DELETE)


@pytest.fixture
def deleted_chamber() -> Chamber:
    """Return a deleted Chamber."""
    new_chamber = ChamberFactory()
    new_chamber.delete()
    return new_chamber


@pytest.fixture
def chamber() -> Chamber:
    """Return a chamber."""
    return ChamberFactory()


@pytest.fixture
def other_chamber() -> Chamber:
    """Return another chamber."""
    return ChamberFactory()


@pytest.fixture
def live_campaign(chamber: Chamber) -> Campaign:
    """Create a live campaign within chamber."""
    return CampaignFactory(chamber=chamber, status=Campaign.STATUSES.LIVE)


@pytest.fixture
def completed_campaign(chamber: Chamber) -> Campaign:
    """Return a `completed` campaign."""
    return CampaignFactory(chamber=chamber, status=Campaign.STATUSES.DONE)


@pytest.fixture
def product_categories(completed_campaign: Campaign) -> list[ProductCategory]:
    """Return list of product categories for testing."""
    return ProductCategoryFactory.create_batch(2, campaign=completed_campaign)


@pytest.fixture
def chamber_full_campaign_data_for_renew(
    completed_campaign: Campaign,
    product_categories: list[ProductCategory],
) -> None:
    """Prepare full chamber's campaign data for renew process."""
    for category in product_categories:
        ProductFactory.create_batch(2, category=category)
    incentives = IncentiveFactory.create_batch(2, campaign=completed_campaign)
    for incentive in incentives:
        IncentiveQualifierFactory.create_batch(2, incentive=incentive)
    teams = TeamFactory.create_batch(2, campaign=completed_campaign)
    for team in teams:
        UserCampaignFactory.create_batch(
            size=2,
            team=team,
            campaign=completed_campaign,
        )
    users = UserCampaign.objects.filter(
        campaign=completed_campaign,
        team__in=teams,
    )
    for user in users:
        ContractFactory.create_batch(
            size=2,
            created_by=user,
            campaign=completed_campaign,
            status=Contract.STATUSES.APPROVED,
        )
    for product in Product.objects.filter(category__in=product_categories):
        LevelFactory.create_batch(2, product=product)
    contracts = Contract.objects.filter(campaign=completed_campaign)
    levels = Level.objects.filter(product__category__in=product_categories)
    for level, contract in zip(levels, contracts):
        LevelInstanceFactory.create_batch(2, level=level, contract=contract)
