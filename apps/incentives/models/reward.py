from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class Reward(BaseModel):
    """Reward that volunteer achieves when passing an incentive's threshold."""

    incentive = models.ForeignKey(
        to="incentives.Incentive",
        verbose_name=_("Incentive"),
        related_name="rewards",
        on_delete=models.CASCADE,
    )
    user_campaign = models.ForeignKey(
        to="campaigns.UserCampaign",
        verbose_name=_("User Campaign"),
        related_name="rewards",
        on_delete=models.CASCADE,
    )
    paid_at = models.DateTimeField(
        verbose_name=_("Paid at"),
        null=True,
        blank=True,
    )
    external_id = models.IntegerField(
        verbose_name=_("ID in old DB"),
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Reward")
        verbose_name_plural = _("Rewards")

    def __str__(self) -> str:
        return (
            f"Reward for "
            f"{self.user_campaign.first_name} {self.user_campaign.last_name}"
        )
