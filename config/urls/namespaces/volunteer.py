from django.urls import path, include
from apps.campaigns.api.volunteer.views import ProfileViewSet
from apps.campaigns.api.volunteer.urls import urlpatterns as campaign_urls
from apps.chambers.api.volunteer.urls import urlpatterns as chamber_urls
from apps.resources.api.volunteer.urls import urlpatterns as resource_urls
from apps.members.api.volunteer.urls import urlpatterns as member_urls


app_name = "volunteer"


urlpatterns = [
    path("auth/", include("apps.users.api.auth.urls.volunteer")),
    path(
        "me/",
        ProfileViewSet.as_view({"get": "retrieve", "put": "update"}),
        name="profile",
    ),
]

urlpatterns += chamber_urls + resource_urls + member_urls + campaign_urls
