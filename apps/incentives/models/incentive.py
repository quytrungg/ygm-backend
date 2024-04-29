import typing

from django.db import models
from django.utils.translation import gettext_lazy as _

from ordered_model.models import OrderedModel, OrderedModelManager
from safedelete.managers import (
    SafeDeleteAllManager,
    SafeDeleteDeletedManager,
    SafeDeleteManager,
)

from apps.core.models import BaseModel

from ..constants import IncentiveType
from ..querysets import IncentiveQuerySet


class IncentiveManager(SafeDeleteManager, OrderedModelManager):
    """Provide custom manager for Incentive model."""


class IncentiveAllManager(SafeDeleteAllManager, OrderedModelManager):
    """Provide custom all manager for Incentive model."""


class IncentiveyDeletedManager(SafeDeleteDeletedManager, OrderedModelManager):
    """Provide custom deleted manager for Incentive model."""


class Incentive(OrderedModel, BaseModel):
    """Represent an incentive in DB.

    Attributes:
        - name: name of incentive
        - threshold: threshold of incentive
        - value: value of incentive
        - type: type of incentive
        - campaign: campaign id that incentive belongs to

    """

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    threshold = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
    )
    value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
    )
    type = models.CharField(
        verbose_name=_("Type"),
        max_length=20,
        choices=IncentiveType.choices,
    )
    campaign = models.ForeignKey(
        to="campaigns.Campaign",
        verbose_name=_("Campaign ID"),
        related_name="incentives",
        on_delete=models.CASCADE,
    )
    external_id = models.IntegerField(
        verbose_name=_("ID in old DB"),
        blank=True,
        null=True,
    )

    objects = IncentiveManager(queryset_class=IncentiveQuerySet)
    all_objects = IncentiveAllManager(queryset_class=IncentiveQuerySet)
    deleted_objects = IncentiveyDeletedManager(
        queryset_class=IncentiveQuerySet,
    )
    order_with_respect_to = "campaign"

    class Meta(OrderedModel.Meta):
        verbose_name = _("Incentive")
        verbose_name_plural = _("Incentives")

    def __str__(self) -> str:
        return self.name

    # pylint: disable=attribute-defined-outside-init
    def delete(self, *args, extra_update=None, **kwargs):
        """Overwrite delete method to return data after delete.

        OrderedModel's delete method returns None when delete objects, causing
        error when parent object (Camapaign is parent of ProductCategory) is
        deleted along with the related/children objects.

        See safedelete/models.py at line 237.

        """
        self._was_deleted_via_delete_method = True

        qs = self.get_ordering_queryset()
        extra_update = {} if extra_update is None else extra_update
        qs.above_instance(self).decrease_order(**extra_update)
        return super(BaseModel, self).delete(*args, **kwargs)

    TYPES = IncentiveType

    # pylint: disable=invalid-name, attribute-defined-outside-init
    def renew(self, campaign) -> typing.Self:
        """Renew an incentive."""
        self.campaign = campaign
        self.id = None
        return self

    def _is_surpassed_by(self, value) -> bool:
        """Check if incentive's threshold is suppressed by `value`."""
        return self.threshold <= value

    def is_achieved_by(self, volunteer) -> bool:
        """Check if the volunteer has satisfied the incentive's condition."""
        if self.type == IncentiveType.TRADE:
            return self._is_surpassed_by(volunteer.total_trade_revenue)
        if self.type == IncentiveType.CASH:
            return self._is_surpassed_by(volunteer.total_cash_revenue)
        return False
