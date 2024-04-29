from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CampaignsAppConfig(AppConfig):
    """Default configuration for Campaigns app."""

    name = "apps.campaigns"
    verbose_name = _("Campaigns")

    def ready(self) -> None:
        #  pylint: disable=unused-import
        from . import signals  # noqa
        from .api import scheme  # noqa
