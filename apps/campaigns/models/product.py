import typing

from django.db import models
from django.utils.translation import gettext_lazy as _

from ordered_model.models import OrderedModel, OrderedModelManager
from safedelete.managers import (
    SafeDeleteAllManager,
    SafeDeleteDeletedManager,
    SafeDeleteManager,
)

from apps.campaigns.querysets import ProductQuerySet
from apps.core.models import BaseModel


class ProductManager(SafeDeleteManager, OrderedModelManager):
    """Provide custom manager for Product model."""


class ProductAllManager(SafeDeleteAllManager, OrderedModelManager):
    """Provide custom all manager for Product model."""


class ProductDeletedManager(SafeDeleteDeletedManager, OrderedModelManager):
    """Provide custom deleted manager for Product model."""


class Product(OrderedModel, BaseModel):
    """Represent products of a campaign in DB.

    Attributes:
        - name: product name
        - pre_trc_income: pre trc income of a product
        - description: product description
        - is_included_in_renewal: indicate whether this product will be
        included in renewal
        - category: category id that product belongs to

    """

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    pre_trc_income = models.DecimalField(
        verbose_name=_("Pre TRC Income"),
        decimal_places=2,
        max_digits=15,
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
    )
    is_included_in_renewal = models.BooleanField(
        verbose_name=_("Included In Renewal"),
        default=True,
    )
    category = models.ForeignKey(
        to="campaigns.ProductCategory",
        verbose_name=_("Product Category ID"),
        related_name="products",
        on_delete=models.CASCADE,
    )
    external_id = models.IntegerField(
        verbose_name=_("ID in old DB"),
        blank=True,
        null=True,
    )

    objects = ProductManager(queryset_class=ProductQuerySet)
    all_objects = ProductAllManager(queryset_class=ProductQuerySet)
    deleted_objects = ProductDeletedManager(queryset_class=ProductQuerySet)
    order_with_respect_to = "category"

    class Meta(OrderedModel.Meta):
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self) -> str:
        return self.name

    # pylint: disable=attribute-defined-outside-init
    def delete(self, *args, extra_update=None, **kwargs):
        """Overwrite delete method to return data after delete.

        OrderedModel's delete method returns None when delete objects, causing
        error when parent object (ProductCategory is parent of Product) is
        deleted along with the related/children objects.

        See safedelete/models.py at line 237.

        """
        self._was_deleted_via_delete_method = True

        qs = self.get_ordering_queryset()
        extra_update = {} if extra_update is None else extra_update
        qs.above_instance(self).decrease_order(**extra_update)
        return super(BaseModel, self).delete(*args, **kwargs)

    # pylint: disable=invalid-name, attribute-defined-outside-init
    def renew(self, category) -> typing.Self:
        """Renew a product."""
        self.category = category
        self.id = None
        return self
