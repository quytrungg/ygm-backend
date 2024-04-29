from django.urls import include, path
from s3direct.api.views import S3DirectWrapper
from apps.chambers.api.public.views import ChamberSubdomainValidateAPIView


app_name = "api"


urlpatterns = [
    path("auth/", include("apps.users.api.auth.urls.common")),
    path(
        "admin/",
        include("config.urls.namespaces.admin", namespace="super-admin"),
    ),
    path(
        "chamber/",
        include("config.urls.namespaces.chamber", namespace="chamber"),
    ),
    path(
        "volunteer/",
        include("config.urls.namespaces.volunteer", namespace="volunteer"),
    ),
    path(
        "public/",
        include("config.urls.namespaces.public", namespace="public"),
    ),
    path(
        "s3/get_upload_params/",
        S3DirectWrapper.as_view(),
        name="get_s3_upload_params",
    ),
    path(
        "chamber-subdomain-existence/",
        ChamberSubdomainValidateAPIView.as_view(),
        name="chamber-subdomain-existence",
    ),
]
