from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

MAX_PHONE_NUMBER_LENGTH = 20
MAX_ZIP_CODE_LENGTH = 15


class AvailableTimezone(TextChoices):
    """Represent supported timezones."""

    US_CENTRAL = "US/Central", _("US/Central")
    US_PACIFIC = "US/Pacific", _("US/Pacific")
    US_MOUNTAIN = "US/Mountain", _("US/Mountain")
    US_EASTERN = "US/Eastern", _("US/Eastern")
