from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ChambersAppConfig(AppConfig):
    """Default configuration for Chambers app."""

    name = "apps.chambers"
    verbose_name = _("Chambers")

    def ready(self) -> None:
        # pylint: disable=unused-import
        from .api import scheme  # noqa
