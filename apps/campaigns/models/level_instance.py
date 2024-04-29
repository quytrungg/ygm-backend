import typing

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class LevelInstance(BaseModel):
    """Represent an instance of a level.

    Attributes:
        - level: level id that this instance belongs to
        - contract: contract id that this instance belongs to
        - cost: cost of this level instance

    """

    level = models.ForeignKey(
        to="campaigns.Level",
        verbose_name=("Level ID"),
        related_name="instances",
        on_delete=models.CASCADE,
    )
    contract = models.ForeignKey(
        to="members.Contract",
        verbose_name=_("Contract ID"),
        related_name="levels",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    cost = models.DecimalField(
        verbose_name=_("Cost"),
        decimal_places=2,
        max_digits=15,
    )
    trade_with = models.CharField(
        verbose_name=_("Trade with"),
        max_length=255,
        default="",
        blank=True,
    )
    declined_at = models.DateTimeField(
        verbose_name=_("Declined At"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Level Instance")
        verbose_name_plural = _("Level Instances")

    def __str__(self) -> str:
        return f"{self.contract} - {self.level}: {self.cost}"

    # pylint: disable=invalid-name, attribute-defined-outside-init
    def renew(self, level) -> typing.Self:
        """Renew new level instance with level & contract for new campaign."""
        self.level = level
        self.declined_at = None
        self.contract = None
        self.id = None
        return self

    def decline(self) -> None:
        """Mark level as declined, update declined_at field."""
        self.declined_at = timezone.now()
        self.save()

    @classmethod
    def from_level(cls, level):
        """Return a LevelInstance from level's information."""
        return cls(
            level=level,
            cost=level.cost,
            contract_id=None,
            declined_at=None,
        )
