import re

from ordered_model.models import OrderedModel


def get_order_for_new_instance(instance: OrderedModel) -> int:
    """Get order for new instance."""
    max_order = instance.get_ordering_queryset().get_max_order()
    return max_order + 1


def normalize_phone_number(phone_number: str) -> str:
    """Return normalized phone numbers."""
    return re.sub(r"\D", "", phone_number)
