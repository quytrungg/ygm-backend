from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

CHAMBER_SUBDOMAIN_MAX_LENGTH = 63
VALID_SUBDOMAIN_PATTERN = r"^[A-Za-z0-9].*[A-Za-z0-9]$"


class ChamberRenewConfig(TextChoices):
    """Represent renew config in chamber."""

    INVENTORY = "inventory", _("Inventory")
    INCENTIVES = "incentives", _("Incentive Schedule")
    USERS = "users", _("User Setup")
    CONTRACTS = "contracts", _("Contracts")
