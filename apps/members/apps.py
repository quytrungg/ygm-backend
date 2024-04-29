from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MembersAppConfig(AppConfig):
    """Default configuration for Members app."""

    name = "apps.members"
    verbose_name = _("Members")

    def ready(self) -> None:
        # pylint: disable=unused-import
        from .api import scheme  # noqa
