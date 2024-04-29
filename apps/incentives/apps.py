from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class IncentivesAppConfig(AppConfig):
    """Default configuration for Incentives app."""

    name = "apps.incentives"
    verbose_name = _("Incentives")

    def ready(self):
        # pylint: disable=unused-import
        from .api import scheme  # noqa
