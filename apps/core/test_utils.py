import dataclasses

from rest_framework import test

from apps.campaigns.factories import UserCampaignFactory
from apps.campaigns.models import Campaign
from apps.users.factories import VolunteerFactory


def get_test_file_url(path: str) -> str:
    """Add localhost to relative URI."""
    if path.startswith("/"):
        return f"http://localhost:8000{path}"
    return f"http://localhost:8000/{path}"


def create_volunteer(campaign: Campaign, **kwargs):
    """Return a volunteer user."""
    user = VolunteerFactory(chamber=campaign.chamber)
    return UserCampaignFactory(user=user, campaign=campaign, **kwargs)


@dataclasses.dataclass(frozen=True, slots=True)
class TestLevelData:
    """Represent data to create test levels."""

    level_info: dict
    total_count: int
    sold_count: int = 0
    declined_count: int = 0


class CAAPIClient(test.APIClient):
    """Provide additional methods for the test client."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campaign = None

    def select_campaign(self, campaign: Campaign):
        """Set currently selected campaign for the API."""
        self.campaign = campaign

    # pylint: disable=too-many-arguments
    def generic(
        self,
        method,
        path,
        data="",
        content_type="application/octet-stream",
        secure=False,
        **extra,
    ):
        """Set the currently selected campaign id for the APIs."""
        if self.campaign:
            headers = extra.get("headers", {})
            headers.update(
                {"campaign": self.campaign.id},
            )
            extra["headers"] = headers
        return super().generic(
            method, path, data, content_type, secure, **extra,
        )
