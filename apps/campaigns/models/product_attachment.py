import typing

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ordered_model.models import OrderedModel, OrderedModelManager
from safedelete import HARD_DELETE
from safedelete.managers import (
    SafeDeleteAllManager,
    SafeDeleteDeletedManager,
    SafeDeleteManager,
)

from apps.core.models import BaseMedia, BaseModel

from ..querysets import ProductAttachmentQuerySet


class ProductAttachmentManager(SafeDeleteManager, OrderedModelManager):
    """Provide custom manager for ProductAttachment model."""


class ProductAttachmentAllManager(SafeDeleteAllManager, OrderedModelManager):
    """Provide custom all manager for ProductAttachment model."""


class ProductAttachmentDeletedManager(
    SafeDeleteDeletedManager,
    OrderedModelManager,
):
    """Provide custom deleted manager for ProductAttachment model."""


class ProductAttachment(OrderedModel, BaseMedia):
    """Represent attachment for products in DB.

    Attributes:
        - name: product attachment name
        - file: attachment file of product
        - content_type: attachment file type
        - product: product id that this attachment belongs to

    """

    _safedelete_policy = HARD_DELETE

    product = models.ForeignKey(
        to="campaigns.Product",
        verbose_name=_("Product ID"),
        related_name="attachments",
        on_delete=models.CASCADE,
    )
    file = models.FileField(   # noqa: DJ01
        verbose_name=_("Media File"),
        max_length=1000,
        blank=True,
        null=True,
    )
    content_type = models.CharField(
        verbose_name=_("Content Type"),
        max_length=255,
    )
    external_url = models.URLField(
        verbose_name=_("External URL"),
        max_length=255,
        blank=True,
    )
    objects = ProductAttachmentManager(
        queryset_class=ProductAttachmentQuerySet,
    )
    all_objects = ProductAttachmentAllManager(
        queryset_class=ProductAttachmentQuerySet,
    )
    deleted_objects = ProductAttachmentDeletedManager(
        queryset_class=ProductAttachmentQuerySet,
    )
    order_with_respect_to = "product"

    class Meta(OrderedModel.Meta):
        verbose_name = _("Product Attachment")
        verbose_name_plural = _("Product Attachments")

    def __str__(self) -> str:
        return self.name

    def clean(self):
        """Clean data before saving.

        Ensure `file` and `external_link` are mutually exclusive, and at least
        one is present.

        """
        if self.file and self.external_url:
            raise ValidationError(
                _("`file` and `external_url` are mutually exclusive."),
            )
        if not (self.file or self.external_url):
            raise ValidationError(
                _("`Either file` or `external_url` must be present."),
            )

    # pylint: disable=attribute-defined-outside-init
    def delete(self, *args, extra_update=None, **kwargs):
        """Overwrite delete method to return data after delete.

        OrderedModel's delete method returns None when delete objects, causing
        error when parent object (Product is parent of ProductAttachment) is
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
        """Return a renewed product attachment."""
        self.product = product
        self.id = None
        return self
