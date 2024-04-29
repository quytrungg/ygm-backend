from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel

from ..constants import InvoiceStatus


class Invoice(BaseModel):
    """Represent invoices from contracts in DB.

    Attributes:
        - name: invoice's name
        - is_paid: indicate whether the invoice has been paid.
        - contract: contract which this invoice is generated from.
        - sent_at: indicate datetime that invoice has been sent
        - number: auto-generated value when the invoice is created.

    """

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=300,
    )
    contract = models.ForeignKey(
        to="members.Contract",
        verbose_name=_("Contract"),
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    is_paid = models.BooleanField(
        verbose_name=_("Is paid"),
        default=False,
    )
    sent_at = models.DateTimeField(
        verbose_name=_("Sent at"),
        null=True,
    )

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")

    def __str__(self) -> str:
        return f"Invoice #{self.pk}"

    def mark_paid(self) -> None:
        """Mark invoice as paid."""
        self.is_paid = True
        self.save()

    STATUSES = InvoiceStatus

    @property
    def status(self) -> str:
        """Return invoice's current status."""
        if self.is_paid:
            return InvoiceStatus.PAID
        if self.sent_at:
            return InvoiceStatus.SENT
        return InvoiceStatus.CREATED
