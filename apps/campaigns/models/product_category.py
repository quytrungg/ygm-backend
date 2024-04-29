import typing

from django.db import models
from django.utils.translation import gettext_lazy as _

from ordered_model.models import OrderedModel, OrderedModelManager
from safedelete.managers import (
    SafeDeleteAllManager,
    SafeDeleteDeletedManager,
    SafeDeleteManager,
)

from apps.campaigns.querysets import ProductCategoryQuerySet
from apps.core.models import BaseModel


class ProductCategoryManager(SafeDeleteManager, OrderedModelManager):
    """Provide custom manager for Product Category model."""


class ProductCategoryAllManager(SafeDeleteAllManager, OrderedModelManager):
    """Provide custom all manager for Product Category model."""


class ProductCategoryDeletedManager(
    SafeDeleteDeletedManager,
    OrderedModelManager,
):
    """Provide custom deleted manager for Product Category model."""


class ProductCategory(OrderedModel, BaseModel):
    """Represent product categories in DB.

    Attributes:
        - name: product category name
        - image: image of a product category
        - campaign: campaign id that category belongs to

    """

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    image = models.ImageField(  # noqa: DJ01
        verbose_name=_("Image"),
        max_length=1000,
        blank=True,
        null=True,
    )
    background_color = models.CharField(
        verbose_name=_("Background Color"),
        max_length=7,
        blank=True,
    )
    campaign = models.ForeignKey(
        to="campaigns.Campaign",
        verbose_name=("Campaign ID"),
        related_name="product_categories",
        on_delete=models.CASCADE,
    )
    external_id = models.IntegerField(
        verbose_name=_("ID in old DB"),
        blank=True,
        null=True,
    )

    objects = ProductCategoryManager(queryset_class=ProductCategoryQuerySet)
    all_objects = ProductCategoryAllManager(
        queryset_class=ProductCategoryQuerySet,
    )
    deleted_objects = ProductCategoryDeletedManager(
        queryset_class=ProductCategoryQuerySet,
    )
    order_with_respect_to = "campaign"

    class Meta(OrderedModel.Meta):
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")

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

    # pylint: disable=invalid-name, attribute-defined-outside-init
    def renew(self, campaign) -> typing.Self:
        """Renew a product category."""
        self.campaign = campaign
        self.id = None
        return self
