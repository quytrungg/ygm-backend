from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class UserPreference(BaseModel):
    """Model for storing user preferences."""

    user = models.OneToOneField(
        to="users.User",
        on_delete=models.CASCADE,
        related_name="preference",
    )
    favorite_candy = models.TextField(
        verbose_name=_("Favorite candy"),
        blank=True,
    )
    favorite_drink = models.TextField(
        verbose_name=_("Favorite drink"),
        blank=True,
    )
    favorite_restaurant = models.TextField(
        verbose_name=_("Favorite restaurant"),
        blank=True,
    )
    favorite_movie = models.TextField(
        verbose_name=_("Favorite movie"),
        blank=True,
    )
    hobbies = models.TextField(
        verbose_name=_("Hobbies"),
        blank=True,
    )
    instagram_url = models.URLField(
        verbose_name=_("Instagram URL"),
        max_length=255,
        blank=True,
    )
    facebook_url = models.URLField(
        verbose_name=_("Facebook URL"),
        max_length=255,
        blank=True,
    )
    twitter_url = models.URLField(
        verbose_name=_("Twitter URL"),
        max_length=255,
        blank=True,
    )
    linkedin_url = models.URLField(
        verbose_name=_("LinkedIn URL"),
        max_length=255,
        blank=True,
    )

    class Meta:
        verbose_name = _("User Preference")
        verbose_name_plural = _("User Preferences")

    def __str__(self) -> str:
        return f"{self.user.email}'s preference"
