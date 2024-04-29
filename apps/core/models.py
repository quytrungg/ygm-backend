import typing

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from safedelete import HARD_DELETE, SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel


class BaseModel(SafeDeleteModel, TimeStampedModel):
    """Base model for apps' models.

    This class adds to models created and modified fields

    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        abstract = True

    def clean(self):
        """Validate model data.

        First we collect all errors as dict and then if there any errors, we
        pass them ValidationError and raise it. By doing this django admin and
        drf can specify for each field an error.

        """
        super().clean()
        errors = {}
        for field in self._meta.fields:
            clean_method = f"clean_{field.name}"
            if hasattr(self, clean_method):
                try:
                    getattr(self, clean_method)()
                except ValidationError as error:
                    errors[field.name] = error
        if errors:
            raise ValidationError(errors)

    def hard_delete(self):
        """Hard delete the object."""
        return self.delete(force_policy=HARD_DELETE)


BaseModelAncestor = typing.TypeVar("BaseModelAncestor", bound=BaseModel)


class BaseMedia(BaseModel):
    """Abstract model for media resources."""

    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
    )
    file = models.FileField(
        verbose_name=_("Media File"),
        max_length=1000,
        blank=True,
    )

    class Meta:
        abstract = True
