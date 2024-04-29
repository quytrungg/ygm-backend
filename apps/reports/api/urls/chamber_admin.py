from rest_framework.routers import DefaultRouter

from apps.reports.api.views import SaleReportViewSet

router = DefaultRouter()
router.register("sales", SaleReportViewSet, basename="sale")
urlpatterns = router.urls
