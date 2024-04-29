from django.apps import AppConfig


class CoreAppConfig(AppConfig):
    """Default configuration for Core app."""

    name = "apps.core"

    def ready(self):
        # pylint: disable=unused-import
        from libs.s3 import scheme  # noqa
