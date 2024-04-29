from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HistoricalDataConfig(AppConfig):
    """Default app config for historical_data app."""

    name = "apps.historical_data"
    verbose_name = _("Historical")
