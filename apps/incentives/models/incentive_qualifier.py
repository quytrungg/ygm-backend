import typing

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel

from ..constants import IncentiveQualifierAmount, IncentiveQualifierName


class IncentiveQualifier(BaseModel):
    """Represent an incentive qualifier in DB.

    Attributes:
        - name: name of incentive qualifier
        - amount: amount of incentive qualifier
        - incentive: incentive id that incentive qualifier belongs to

    """

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=20,
        choices=IncentiveQualifierName.choices,
    )
    amount = models.IntegerField(
        verbose_name=_("Amount"),
        choices=IncentiveQualifierAmount.choices,
    )
    incentive = models.ForeignKey(
        to="incentives.Incentive",
        verbose_name=_("Incentive ID"),
        related_name="qualifiers",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Incentive Qualifier")
        verbose_name_plural = _("Incentive Qualifiers")

    def __str__(self) -> str:
        return f"{self.name} for {self.incentive.name}"

    # pylint: disable=invalid-name, attribute-defined-outside-init
    def renew(self, incentive) -> typing.Self:
        """Renew an incentive qualifier."""
        self.incentive = incentive
        self.id = None
        return self
