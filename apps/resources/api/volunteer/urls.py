from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("resources", views.ResourceViewSet, basename="resource")

urlpatterns = router.urls
