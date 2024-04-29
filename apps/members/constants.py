from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class ContractStatus(TextChoices):
    """Possible User Roles."""

    DRAFT = "draft", _("Draft")
    APPROVED = "approved", _("Approved")
    SENT = "sent", _("Sent")
    DECLINED = "declined", _("Declined")
    SIGNED = "signed", _("Signed")

    @classmethod
    def get_order_by_approval_priority(cls):
        """Return order by approval priority."""
        return (
            cls.SIGNED,
            cls.SENT,
            cls.DRAFT,
            cls.APPROVED,
            cls.DECLINED,
        )


class ContractType(TextChoices):
    """Represent contract's type."""

    CASH = "cash", _("Cash")
    TRADE = "trade", _("Trade")


class InvoiceStatus(TextChoices):
    """Represent invoice's statuses."""

    CREATED = "created", _("Created")
    SENT = "sent", _("Sent")
    PAID = "paid", _("Paid")
