from ordered_model.models import OrderedModelQuerySet
from safedelete.queryset import SafeDeleteQueryset


class ProductAttachmentQuerySet(OrderedModelQuerySet, SafeDeleteQueryset):
    """Provide custom queryset for ProductAttachment model."""
