import typing
import urllib.parse

from libs.utils import get_latest_version
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

ENDPOINTS_TO_FILTER_OUT = [
    # Motivation:
    # This endpoint is called often by AWS EC2 target group checker or via k8s
    # checker, so it sends a lot of data to sentry,
    # while this endpoint actually does nothing
    "liveness",
]


def is_filter_out_endpoint(event: dict[str, typing.Any]) -> bool:
    """Return True if endpoint's data doesn't need to be sent in sentry."""
    # For celery tasks
    if "request" not in event:
        return False

    url_string = event["request"]["url"]
    parsed_url = urllib.parse.urlparse(url_string)

    return parsed_url.path.strip("/") in ENDPOINTS_TO_FILTER_OUT


def before_send_transaction(
    event: dict[str, typing.Any],
    hint: dict[str, typing.Any],
) -> dict[str, typing.Any] | None:
    """Delete personal user info and remove redundant endpoints."""
    # Settings imported here to avoid circular imports
    from django.conf import settings
    if settings.TESTING:
        return

    if is_filter_out_endpoint(event):
        return
    return event


# https://docs.sentry.io/platforms/python/guides/django/
SENTRY_CONFIG = {
    # Adds django, celery, redis support
    "integrations": (
        DjangoIntegration(),
        CeleryIntegration(),
        RedisIntegration(),
    ),
    "attach_stacktrace": True,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    "send_default_pii": True,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    "traces_sample_rate": 1.0,
    # Adds a body of request
    "request_bodies": "always",
    "release": get_latest_version("CHANGELOG.md"),
    "before_send_transaction": before_send_transaction,
}
