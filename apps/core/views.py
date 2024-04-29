import platform
from collections import namedtuple

import django
from django.conf import settings
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.views.generic import TemplateView

from libs.permissions import can_access_debug_tools
from libs.utils import get_changelog_html, get_latest_version

Changelog = namedtuple("Changelog", ["name", "text", "version", "open_api_ui"])

ARGO_CD_URL_MAPPING = {
    "development": "https://deploy.saritasa.rocks/",
    "prod": "TODO",
}
ARGO_CD_MAPPING = {
    "development": "ygm-backend-dev",
    "prod": "ygm-backend-prod",
}


class AppStatsMixin:
    """Add information about app to context."""

    def get_context_data(self, **kwargs):
        """Load changelog data from files."""
        context = super().get_context_data(**kwargs)
        context.update(
            show_debug_tools=can_access_debug_tools(self.request.user),
            env=settings.ENVIRONMENT,
            version=get_latest_version("CHANGELOG.md"),
            python_version=platform.python_version(),
            django_version=django.get_version(),
            app_url=settings.FRONTEND_URL,
            app_label=settings.APP_LABEL,
            argo_cd_url=ARGO_CD_URL_MAPPING.get(
                settings.ENVIRONMENT, ARGO_CD_URL_MAPPING["development"],
            ),
            argo_cd_app=ARGO_CD_MAPPING.get(
                settings.ENVIRONMENT, ARGO_CD_MAPPING["development"],
            ),
        )
        return context


class IndexView(AppStatsMixin, TemplateView):
    """Class-based view for that shows version of open_api file on main page.

    Displays the current version of the open_api specification and changelog.

    """

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        """Load changelog data from files."""
        context = super().get_context_data(**kwargs)
        try:
            open_api_ui_url = reverse("open_api:ui")
        except NoReverseMatch:
            open_api_ui_url = None
        context["changelog"] = Changelog(
            name=settings.SPECTACULAR_SETTINGS.get("TITLE"),
            text=get_changelog_html("CHANGELOG.md"),
            version=settings.SPECTACULAR_SETTINGS.get("VERSION"),
            open_api_ui=open_api_ui_url,
        )
        return context
