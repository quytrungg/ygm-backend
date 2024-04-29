import pytest
from safedelete.config import HARD_DELETE

from apps.campaigns.constants import CampaignStatus
from apps.campaigns.factories import CampaignFactory
from apps.campaigns.models import Campaign
from apps.chambers.factories import ChamberFactory
from apps.chambers.models import Chamber
from apps.incentives.constants import (
    IncentiveQualifierAmount,
    IncentiveQualifierName,
    IncentiveType,
)
from apps.incentives.factories import IncentiveFactory
from apps.incentives.models import Incentive
from apps.users.constants import UserRole
from apps.users.factories import UserFactory
from apps.users.models import User


@pytest.fixture
def chamber() -> Chamber:
    """Create a chamber for chamber admin."""
    return ChamberFactory()


@pytest.fixture
def chamber_admin(django_db_blocker, chamber: Chamber) -> User:
    """Create a chamber admin."""
    with django_db_blocker.unblock():
        user = UserFactory(role=UserRole.CHAMBER_ADMIN, chamber=chamber)
        yield user
        user.delete(force_policy=HARD_DELETE)


@pytest.fixture
def campaign(chamber: Chamber) -> Campaign:
    """Create a campaign for chamber."""
    return CampaignFactory(chamber=chamber, status=CampaignStatus.CREATED)


@pytest.fixture
def incentive(campaign: Campaign) -> Incentive:
    """Create an incentive for campaign."""
    return IncentiveFactory(campaign=campaign)


@pytest.fixture
def incentive_data() -> dict:
    """Return data for creating & updating an incentive."""
    return {
        "name": "Test Incentive",
        "threshold": 100,
        "value": 20,
        "type": IncentiveType.CASH,
        "qualifiers": [
            {
                "name": IncentiveQualifierName.SELLS,
                "amount": IncentiveQualifierAmount.AMOUNT_10,
            },
            {
                "name": IncentiveQualifierName.AMOUNT,
                "amount": IncentiveQualifierAmount.AMOUNT_100,
            },
        ],
    }
