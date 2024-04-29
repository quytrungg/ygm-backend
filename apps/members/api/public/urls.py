from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(
    r"purchasing-members",
    viewset=views.PurchasingMemberViewSet,
    basename="purchasing-members",
)
router.register(
    r"contracts",
    viewset=views.ContractViewSet,
    basename="contract",
)

urlpatterns = router.urls
