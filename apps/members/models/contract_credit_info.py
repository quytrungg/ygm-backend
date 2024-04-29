import typing

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_extensions.db.models import TimeStampedModel


class ContractCreditInfo(TimeStampedModel):
    """Represent credit relationship of contracts and volunteers."""

    contract = models.ForeignKey(
        to="members.Contract",
        verbose_name=_("Contract"),
        on_delete=models.CASCADE,
        related_name="credits_info",
    )
    user_campaign = models.ForeignKey(
        to="campaigns.UserCampaign",
        verbose_name=_("User campaign"),
        on_delete=models.DO_NOTHING,
        related_name="contracts_credit_info",
    )
    portion = models.DecimalField(
        verbose_name=_("Portion"),
        decimal_places=14,
        max_digits=15,
    )

    class Meta:
        verbose_name = _("Contract Credit Info")
        verbose_name_plural = _("Contract Credits Info")

    def __str__(self):
        return f"{self.contract} - {self.user_campaign}"

    # pylint: disable=invalid-name, attribute-defined-outside-init
    def renew(self, contract, user_campaign) -> typing.Self:
        """Duplicate contract credit info for renewed campaign."""
        self.contract = contract
        self.user_campaign = user_campaign
        self.id = None
        return self

    def reassign(self, user) -> typing.Self:
        """Update credit info for reassigned contract."""
        self.user_campaign = user
        return self
