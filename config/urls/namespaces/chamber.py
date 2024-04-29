from django.urls import path, include
from apps.users.api.views import ProfileCAViewSet
from apps.campaigns.api.chamber_admin.urls import urlpatterns as campaign_urls
from apps.chambers.api.chamber_admin.urls import urlpatterns as chamber_urls
from apps.timelines.api.chamber_admin.urls import urlpatterns as timeline_urls
from apps.resources.api.chamber_admin.urls import urlpatterns as resource_urls
from apps.members.api.chamber_admin.urls import urlpatterns as member_urls
from apps.incentives.api.chamber_admin.urls import (
    urlpatterns as incentive_urls,
)


app_name = "chamber"

urlpatterns = [
    path("auth/", include("apps.users.api.auth.urls.chamber_admin")),
    path("reports/", include("apps.reports.api.urls.chamber_admin")),
    path(
        "me/",
        ProfileCAViewSet.as_view({"get": "retrieve", "put": "update"}),
        name="profile",
    ),
]

urlpatterns += (
    chamber_urls
    + campaign_urls
    + timeline_urls
    + resource_urls
    + member_urls
    + incentive_urls
)
