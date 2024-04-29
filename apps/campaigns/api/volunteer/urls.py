from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(
    "dashboard", views.CampaignViewSet, basename="dashboard",
)
router.register(
    "dashboard/recently-sold",
    views.RecentlySoldLevelInstanceViewSet,
    basename="recently-sold",
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
    "remaining-sponsorship",
    views.RemainingSponsorshipViewSet,
    basename="remaining-sponsorship",
)
router.register(
    "users",
    views.UserCampaignViewSet,
    basename="user-campaign",
)

urlpatterns = router.urls
