import typing

from django.db import models
from django.utils.translation import gettext_lazy as _

from ordered_model.models import OrderedModel, OrderedModelManager
from safedelete.managers import (
    SafeDeleteAllManager,
    SafeDeleteDeletedManager,
    SafeDeleteManager,
)

from apps.campaigns.querysets import LevelQuerySet
from apps.core.models import BaseModel


class LevelManager(SafeDeleteManager, OrderedModelManager):
    """Provide custom manager for Order model."""


class LevelAllManager(SafeDeleteAllManager, OrderedModelManager):
    """Provide custom all manager for Order model."""


class LevelDeletedManager(SafeDeleteDeletedManager, OrderedModelManager):
    """Provide custom deleted manager for Order model."""


class Level(OrderedModel, BaseModel):
    """Represent levels of a product in DB.

    Attributes:
        - name: level name
        - cost: level cost
        - benefits: benefits of a level
        - description: level description
        - conditions: conditions of a level
        - product: product id that this level belongs to

    """

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    cost = models.DecimalField(
        verbose_name=_("Unit Cost"),
        decimal_places=2,
        max_digits=15,
    )
    amount = models.IntegerField(
        verbose_name=_("Amount"),
    )
    benefits = models.TextField(
        verbose_name=_("Benefits"),
        blank=True,
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
    )
    conditions = models.TextField(
        verbose_name=_("Conditions"),
        blank=True,
    )
    product = models.ForeignKey(
        to="campaigns.Product",
        verbose_name=_("Product ID"),
        related_name="levels",
        on_delete=models.CASCADE,
    )
    external_id = models.IntegerField(
        verbose_name=_("ID in old DB"),
        blank=True,
        null=True,
    )
    external_multiplier = models.DecimalField(
        verbose_name=_("Multiplier in old DB"),
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=5,
    )

    objects = LevelManager(queryset_class=LevelQuerySet)
    all_objects = LevelAllManager(queryset_class=LevelQuerySet)
    deleted_objects = LevelDeletedManager(queryset_class=LevelQuerySet)
    order_with_respect_to = "product"

    class Meta(OrderedModel.Meta):
        verbose_name = _("Level")
        verbose_name_plural = _("Levels")

    def __str__(self) -> str:
        return self.name

    # pylint: disable=attribute-defined-outside-init
    def delete(self, *args, extra_update=None, **kwargs):
        """Overwrite delete method to return data after delete.

        OrderedModel's delete method returns None when delete objects, causing
        error when parent object (Product is parent of Level) is
        deleted along with the related/children objects.

        See safedelete/models.py at line 237.

        """
        self._was_deleted_via_delete_method = True

        qs = self.get_ordering_queryset()
        extra_update = {} if extra_update is None else extra_update
        qs.above_instance(self).decrease_order(**extra_update)
        return super(BaseModel, self).delete(*args, **kwargs)

    # pylint: disable=invalid-name, attribute-defined-outside-init
    def renew(self, product) -> typing.Self:
        """Renew a level with product for new campaign."""
        self.product = product
        self.id = None
        return self
