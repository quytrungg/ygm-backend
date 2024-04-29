from django.db import transaction

from apps.core.services import get_order_for_new_instance

from .. import models


def duplicate_level(level_id: int) -> models.Level:
    """Duplicate level and level instances beneath."""
    with transaction.atomic():
        level = models.Level.objects.filter(
            id=level_id,
        ).select_related("product").first()
        if not level:
            return None
        new_level = level.renew(product=level.product)
        new_level.order = get_order_for_new_instance(level)
        new_level.save()
        return new_level
