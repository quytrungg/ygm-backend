from ordered_model.models import OrderedModelQuerySet
from safedelete.queryset import SafeDeleteQueryset


class IncentiveQuerySet(SafeDeleteQueryset, OrderedModelQuerySet):
    """Provide custom queryset methods for Incentive model."""
