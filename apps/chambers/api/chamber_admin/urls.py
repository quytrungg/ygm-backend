from django.urls import path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(
    "stored-members",
    views.StoredMemberViewSet,
    basename="stored-member",
)
router.register(
    "import-stored-members",
    views.StoredMemberImportViewSet,
    basename="import-stored-member",
)

urlpatterns = [
    path(
        "branding/",
        views.ChamberBrandingViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
            },
        ),
        name="branding",
    ),
    path(
        "dashboard/", views.DashboardAPIView.as_view(), name="dashboard",
    ),
    path(
        "info/",
        views.ChamberViewSet.as_view({
            "get": "retrieve",
            "put": "update",
        }),
        name="info",
    ),
] + router.urls
