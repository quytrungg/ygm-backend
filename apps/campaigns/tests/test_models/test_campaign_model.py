from django.core.exceptions import ValidationError

import pytest

from apps.campaigns.constants import CAMPAIGN_IN_PROGRESS_STATUSES
from apps.campaigns.factories import CampaignFactory
from apps.campaigns.models import Campaign


@pytest.mark.parametrize(
    argnames="existing_campaign",
    argvalues=[
        pytest.lazy_fixture("open_campaign"),
        pytest.lazy_fixture("active_campaign"),
    ],
)
def test_clean_campaign_fail(
    existing_campaign: Campaign,
):
    """Ensure exist only 1 in-progress campaign per chamber at a time."""
    for status in CAMPAIGN_IN_PROGRESS_STATUSES:
        camp = CampaignFactory.build(
            status=status,
            chamber_id=existing_campaign.chamber_id,
        )
        with pytest.raises(ValidationError):
            camp.clean()
