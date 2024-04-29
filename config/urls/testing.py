from apps.core.tests.views import ImpersonateTestViewSet
from rest_framework.routers import DefaultRouter
from django.conf import settings


router = DefaultRouter()
router.register(
    "impersonate",
    ImpersonateTestViewSet,
    basename="impersonate",
)

# Testing urls
urlpatterns = []

if settings.TESTING:
    urlpatterns += router.urls
