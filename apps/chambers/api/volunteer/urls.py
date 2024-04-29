from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(
    "stored-members",
    views.StoredMemberViewSet,
    basename="stored-member",
)

urlpatterns = router.urls
