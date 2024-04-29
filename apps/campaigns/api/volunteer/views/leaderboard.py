from apps.core.api.views import VolunteerBaseViewSet

from ...common.views import (
    LeadershipStandingBaseViewSet,
    TeamStandingBaseViewSet,
    VolunteerStandingBaseViewSet,
)


class VolunteerStandingViewSet(
    VolunteerStandingBaseViewSet,
    VolunteerBaseViewSet,
):
    """Provide logic for Volunteer Standing VS API."""


class LeadershipStandingViewSet(
    LeadershipStandingBaseViewSet,
    VolunteerBaseViewSet,
):
    """Provide logic for Leadership Standing VS API."""


class TeamStandingViewSet(TeamStandingBaseViewSet, VolunteerBaseViewSet):
    """Provide logic for Team Standing VS API."""
