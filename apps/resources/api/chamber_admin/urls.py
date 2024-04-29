from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("resources", views.ResourceViewSet, basename="resource")
router.register(
    "resource-categories",
    views.ResourceCategoryViewSet,
    basename="resource-category",
)

urlpatterns = router.urls
