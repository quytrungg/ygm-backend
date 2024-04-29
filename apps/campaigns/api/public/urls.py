from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(
    "campaigns",
    views.CampaignViewSet,
    basename="campaign",
)
router.register(
    "product-categories",
    views.ProductCategoryViewSet,
    basename="product-category",
)
router.register(
    "products",
    views.ProductViewSet,
    basename="product",
)
router.register(
    "levels",
    views.LevelViewSet,
    basename="level",
)
router.register(
    "purchased-levels",
    views.MemberPurchasedLevelViewSet,
    basename="purchased-levels",
)

urlpatterns = router.urls
