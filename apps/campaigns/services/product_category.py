from decimal import Decimal
from pathlib import Path

from django.core.files.images import ImageFile
from django.db import transaction
from django.db.models import Prefetch

from .. import models
from ..constants import DEFAULT_PRODUCT_CATEGORIES, IMAGE_ROOT_PATH
from ..models import Campaign, Level, ProductCategory


def duplicate_category(category_id: int):
    """Duplicate a product category and products/levels beneath it."""
    with transaction.atomic():
        products_prefetch = Prefetch(
            "products",
            queryset=models.Product.objects.all().for_duplication(),
        )
        category = models.ProductCategory.objects.filter(
            id=category_id,
        ).prefetch_related(products_prefetch).select_related(
            "campaign",
        ).first()
        if not category:
            return None
        products = category.products.all()
        new_category = category.renew(campaign=category.campaign)
        new_category.order = None

        new_products = []
        new_products_attachments = []
        new_levels = []
        for product in products:
            levels = product.levels.all()
            attachments = product.attachments.all()
            new_product = product.renew(category=new_category)
            new_products.append(new_product)
            for level in levels:
                new_level = level.renew(product=new_product)
                new_levels.append(new_level)
            new_products_attachments.extend(
                attachment.renew(new_product)
                for attachment in attachments
            )

        new_category.save()
        models.Product.objects.bulk_create(new_products)
        models.ProductAttachment.objects.bulk_create(new_products_attachments)
        models.Level.objects.bulk_create(new_levels)
        return new_category


def get_product_category_stats(category: ProductCategory) -> dict[Decimal]:
    """Calculate statistics of a given product category."""
    levels = Level.objects.filter(
        product__category_id=category.id,
    ).with_total_instances_count()
    total_value = sum(
        level.cost * level.total_instances_count
        for level in levels
        if level.amount > 0
    )
    return {
        "total_value": total_value,
    }


def create_default_product_categories(campaign: Campaign):
    """Get default product categories for campaign."""
    for category in DEFAULT_PRODUCT_CATEGORIES:
        if image_path := category.image_name:
            path = Path(IMAGE_ROOT_PATH, image_path)
            with open(path, "rb") as image_file:
                ProductCategory.objects.create(
                    name=category.name,
                    image=ImageFile(image_file),
                    campaign=campaign,
                )
            continue

        ProductCategory.objects.create(
            name=category.name,
            background_color=category.background_color,
            campaign=campaign,
        )
