from enum import StrEnum

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class TimelineCategoryNames(StrEnum):
    """Provide names of timeline categories."""

    INCENTIVES_TRIP = "Incentives-Trip"
    MARCOMM = "MarComm"
    RECRUITMENT = "Recruitment"
    TRAININGS = "Trainings"
    TRC_EVENTS = "TRC Events"
    TRC_MANAGEMENT = "TRC Management"
    WRAP_UP = "Wrap-Up"


class TimelineStatus(TextChoices):
    """Provide statuses in a timeline.

    Each timline can have these statuses:
        - not_started: Not Started
        - in_progress: In Progress
        - pending: Pending
        - completed: Completed

    """

    NOT_STARTED = "not_started", _("Not Started")
    IN_PROGRESS = "in_progress", _("In Progress")
    PENDING = "pending", _("Pending")
    COMPLETED = "completed", _("Completed")


class TimelineTypeChoice(TextChoices):
    """Provide possible types in a timeline."""

    WITHOUT_VICE_CHAIR = "23os_tc", _("23OS TC")
    WITH_VICE_CHAIR = "23os_vc", _("23OS VC")
