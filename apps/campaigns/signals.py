from django.db.models.signals import post_save
from django.dispatch import receiver

from . import services
from .models import Campaign


@receiver(post_save, sender=Campaign)
def campaign_post_save(
    instance: Campaign,
    created,
    **kwargs,
):
    """Create default product categories for campaign."""
    if not created or instance.is_renewed:
        return
    services.create_default_product_categories(campaign=instance)
    services.create_default_user_campaign(campaign=instance)
