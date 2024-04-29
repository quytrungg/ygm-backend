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
    "level-instances",
    views.LevelInstanceViewSet,
    basename="level-instance",
)
router.register(
    "volunteer-standings",
    views.VolunteerStandingViewSet,
    basename="volunteer-standing",
)
router.register(
    "team-standings",
    views.TeamStandingViewSet,
    basename="team-standing",
)
router.register(
    "leadership-standings",
    views.LeadershipStandingViewSet,
    basename="leadership-standing",
)
router.register(
    "marketing-opportunities",
    views.MarketingOpportunitiesViewSet,
    basename="marketing-opportunities",
)
router.register(
    "product-attachments",
    views.ProductAttachmentViewSet,
    basename="product-attachment",
)
router.register("notes", views.NoteViewSet, basename="note")
router.register("teams", views.TeamViewSet, basename="team")
router.register("users", views.UserCampaignViewSet, basename="user-campaign")

urlpatterns = router.urls
