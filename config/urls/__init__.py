from django.contrib import admin
from django.urls import include, path

from apps.core.views import IndexView
from libs.health_checks import liveness_check

from .api_versions import urlpatterns as api_urlpatterns
from .debug import urlpatterns as debug_urlpatterns
from .testing import urlpatterns as testing_urlpatterns
from .autocomplete import urlpatterns as autocomplete_urlpatterns

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("mission-control-center/", admin.site.urls),
    # Django Health Check url
    # See more details: https://pypi.org/project/django-health-check/
    # Custom checks at lib/health_checks
    path("health/", include("health_check.urls")),
    path("liveness/", liveness_check.liveness_check, name="liveness"),
]

urlpatterns += api_urlpatterns
urlpatterns += autocomplete_urlpatterns
urlpatterns += debug_urlpatterns
urlpatterns += testing_urlpatterns
