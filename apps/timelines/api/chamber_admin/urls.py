from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("timelines", views.TimelineViewSet, basename="timeline")
router.register(
    "timeline-categories",
    views.TimelineCategoryViewSet,
    basename="timeline-category",
)
router.register(
    "timeline-types",
    views.TimelineTypeViewSet,
    basename="timeline-type",
)

urlpatterns = router.urls
