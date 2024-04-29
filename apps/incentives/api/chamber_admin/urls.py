from django.urls import path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(
    "incentives",
    views.IncentiveViewSet,
    basename="incentive",
)
router.register(
    "rally-session",
    views.RallySessionViewSet,
    basename="rally-session",
)
router.register(
    "paid-and-owed",
    views.PaidAndOwedRewardViewSet,
    basename="paid-and-owed",
)
router.register(
    "rewards",
    views.RewardViewSet,
    basename="reward",
)

urlpatterns = router.urls
urlpatterns += [
    path(
        "reward-payment-status/",
        views.RewardMarkPaymentStatusAPIView.as_view(),
        name="mark-reward-payment-status",
    ),
    path(
        "payout/<int:pk>",
        views.PayoutMetricsAPIView.as_view(),
        name="payout",
    ),
]
