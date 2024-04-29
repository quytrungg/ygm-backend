from ordered_model.models import OrderedModelQuerySet
from safedelete.queryset import SafeDeleteQueryset


class TimelineQuerySet(SafeDeleteQueryset, OrderedModelQuerySet):
    """Provide custom queryset methods for Timeline."""
