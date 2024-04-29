from django.db.models import IntegerChoices, TextChoices
from django.utils.translation import gettext_lazy as _


class IncentiveType(TextChoices):
    """Provide types for an incentive."""

    CASH = "cash", _("Cash")
    TRIP = "trip", _("Trip")
    TRADE = "trade", _("Trade")
    OTHER = "other", _("Other")


class IncentiveQualifierName(TextChoices):
    """Provide names for an incentive qualifier."""

    SELLS = "sells", _("Sells")
    AMOUNT = "amount", _("Amount")
    CLIENTS = "clients", _("Clients")


class IncentiveQualifierAmount(IntegerChoices):
    """Provide default amounts for an incentive qualifier."""

    AMOUNT_10 = 10, _("10")
    AMOUNT_20 = 20, _("20")
    AMOUNT_30 = 30, _("30")
    AMOUNT_100 = 100, _("100")
