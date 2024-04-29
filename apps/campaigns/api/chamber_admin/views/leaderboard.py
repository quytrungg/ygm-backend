from apps.core.api.views import ChamberBaseViewSet

from ...common.views import (
    LeadershipStandingBaseViewSet,
    TeamStandingBaseViewSet,
    VolunteerStandingBaseViewSet,
)


class VolunteerStandingViewSet(
    VolunteerStandingBaseViewSet,
    ChamberBaseViewSet,
):
    """Provide logic for Volunteer Standing CA API."""


class LeadershipStandingViewSet(
    LeadershipStandingBaseViewSet,
    ChamberBaseViewSet,
):
    """Provide logic for Leadership Standing CA API."""


class TeamStandingViewSet(TeamStandingBaseViewSet, ChamberBaseViewSet):
    """Provide logic for Team Standing CA API."""
