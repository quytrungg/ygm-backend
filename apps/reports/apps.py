from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ReportsAppConfig(AppConfig):
    """Default configuration for Reports app."""

    name = "apps.reports"
    verbose_name = _("Reports")
