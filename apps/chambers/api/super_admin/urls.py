from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("chambers", views.ChamberViewSet, basename="chamber")

urlpatterns = router.urls
