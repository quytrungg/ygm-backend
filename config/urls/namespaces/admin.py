from django.urls import path, include
from apps.users.api.views import ProfileSAViewSet
from apps.campaigns.api.super_admin.urls import urlpatterns as campaign_urls
from apps.chambers.api.super_admin.urls import urlpatterns as chamber_urls
from apps.resources.api.super_admin.urls import urlpatterns as resource_urls


app_name = "super-admin"

urlpatterns = chamber_urls + resource_urls + campaign_urls + [
    path("auth/", include("apps.users.api.auth.urls.super_admin")),
    path(
        "me/",
        ProfileSAViewSet.as_view({"get": "retrieve", "put": "update"}),
        name="profile",
    ),
]
