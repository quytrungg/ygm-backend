from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, UserPreference


@receiver(post_save, sender=User)
def add_preference_after_user_creation(instance: User, created, **kwargs):
    """Add preference after user creation."""
    if not created:
        return

    UserPreference.objects.create(user=instance)
