from django.utils.translation import gettext_lazy as _

from rest_framework import status

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from knox.views import LogoutAllView, LogoutView

from libs.open_api.extend_schema import fix_api_view_warning
from libs.open_api.serializers import DetailSerializer

from . import serializers, views


class KnoxTokenScheme(OpenApiAuthenticationExtension):
    """Scheme to describe knox auth scheme."""

    target_class = "knox.auth.TokenAuthentication"
    name = "TokenAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": _(
                "Token-based authentication with required prefix `Token`",
            ),
        }


class CustomTokenScheme(KnoxTokenScheme):
    """Scheme to describe scheme for our custom authentication class."""

    target_class = "apps.core.api.auth.TokenAuthentication"


fix_api_view_warning(views.LoginView)
fix_api_view_warning(views.SuperAdminLoginView)
fix_api_view_warning(views.ChamberAdminLoginView)
fix_api_view_warning(LogoutView)
fix_api_view_warning(LogoutAllView)

extend_schema_view(
    post=extend_schema(
        request=serializers.AuthTokenSerializer,
        responses=serializers.TokenSerializer,
    ),
)(views.SuperAdminLoginView)

extend_schema_view(
    post=extend_schema(
        request=serializers.NonSAAuthTokenSerializer,
        responses=serializers.TokenSerializer,
    ),
)(views.ChamberAdminLoginView)

extend_schema_view(
    post=extend_schema(
        request=serializers.PasswordResetSerializer,
        responses=DetailSerializer,
    ),
)(views.PasswordResetView)

extend_schema_view(
    post=extend_schema(
        request=serializers.PasswordResetConfirmSerializer,
        responses=DetailSerializer,
    ),
)(views.PasswordResetConfirmView)

extend_schema_view(
    post=extend_schema(
        request=serializers.ChamberAdminRegisterSerializer,
        responses={
            status.HTTP_200_OK: serializers.TokenSerializer,
        },
    ),
)(views.ChamberAdminRegisterAPIView)

extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name="uid",
                description="Chamber Admin's uid.",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="token",
                description="Chamber Admin's token.",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
        request=serializers.ChamberAdminRegisterInfoSerializer,
        responses=None,
    ),
)(views.ChamberAdminRegisterInfoAPIView)

extend_schema_view(
    post=extend_schema(
        request=serializers.NonSAAuthTokenSerializer,
        responses=serializers.TokenSerializer,
    ),
)(views.VolunteerLoginView)
