from django.db import transaction

from apps.core.services import get_order_for_new_instance

from .. import models


def duplicate_product(product_id: int):
    """Duplicate a product and levels beneath it."""
    with transaction.atomic():
        product = models.Product.objects.filter(
            id=product_id,
        ).for_duplication().select_related("category").first()
        if not product:
            return None
        levels = product.levels.all()
        attachments = product.attachments.all()

        new_product = product.renew(category=product.category)
        new_product_attachments = []
        new_levels = []
        for level in levels:
            new_level = level.renew(product=new_product)
            new_levels.append(new_level)
        new_product_attachments.extend(
            attachment.renew(new_product)
            for attachment in attachments
        )
        new_product.order = get_order_for_new_instance(product)
        new_product.save()
        models.ProductAttachment.objects.bulk_create(new_product_attachments)
        models.Level.objects.bulk_create(new_levels)
        return new_product
