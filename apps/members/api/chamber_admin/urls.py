from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(
    r"contracts",
    viewset=views.ContractViewSet,
    basename="contract",
)
router.register(
    r"invoices",
    viewset=views.InvoiceViewSet,
    basename="invoice",
)

urlpatterns = router.urls
