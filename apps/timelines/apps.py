from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TimelinesAppConfig(AppConfig):
    """Default configuration for Timelines app."""

    name = "apps.timelines"
    verbose_name = _("Timelines")
