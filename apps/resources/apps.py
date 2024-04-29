from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ResourcesAppConfig(AppConfig):
    """Default configuration for Resources app."""

    name = "apps.resources"
    verbose_name = _("Resources")
