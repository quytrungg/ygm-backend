import typing

from django.db import models
from django.utils.translation import gettext_lazy as _

from safedelete.managers import (
    SafeDeleteAllManager,
    SafeDeleteDeletedManager,
    SafeDeleteManager,
)

from apps.campaigns import querysets as campaigns_querysets
from apps.core.models import BaseModel


class Team(BaseModel):
    """Represent user teams within campaign.

    Groups user in teams for the campaign.

    Attributes
        - name: Name of the team
        - campaign: FK to campaign

    """

    name = models.CharField(
        max_length=255,
        verbose_name=_("Team"),
    )
    goal = models.DecimalField(
        verbose_name=_("Team Goal"),
        decimal_places=2,
        max_digits=15,
        default=0,
    )
    campaign = models.ForeignKey(
        to="campaigns.Campaign",
        on_delete=models.CASCADE,
        verbose_name=_("Campaign"),
    )
    managed_by = models.ForeignKey(
        to="campaigns.UserCampaign",
        on_delete=models.SET_NULL,
        verbose_name=_("Managed by"),
        related_name="managed_teams",
        null=True,
    )
    external_id = models.IntegerField(
        verbose_name=_("ID in old DB"),
        blank=True,
        null=True,
    )

    objects = SafeDeleteManager(
        queryset_class=campaigns_querysets.TeamQuerySet,
    )
    all_objects = SafeDeleteAllManager(
        queryset_class=campaigns_querysets.TeamQuerySet,
    )
    deleted_objects = SafeDeleteDeletedManager(
        queryset_class=campaigns_querysets.TeamQuerySet,
    )

    class Meta:
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")

    def __str__(self):
        return self.name

    # pylint: disable=invalid-name, attribute-defined-outside-init
    def renew(self, campaign) -> typing.Self:
        """Renew a team for new campaign."""
        self.campaign = campaign
        self.id = None
        return self
