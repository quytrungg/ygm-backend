import typing

from django.contrib.auth import login
from django.utils.translation import gettext_lazy as _

from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from knox.views import LoginView as KnoxLoginView

from apps.campaigns.models import Campaign, UserCampaign

from ...constants import UserRole
from . import serializers
from .serializers import (
    get_deactivated_user_campaign_error,
    get_invalid_credentials_error,
)


class LoginView(KnoxLoginView):
    """User authentication view.

    We're using custom one because Knox using basic auth as default
    authorization method.

    """

    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request, *args, **kwargs) -> Response:
        """Login user and get auth token with expiry."""
        serializer = serializers.AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        login(request, serializer.validated_data["user"])
        return super().post(request, format=None)


class PasswordResetView(GenericAPIView):
    """Change user's password on reset.

    If email is valid, simply sends password with link that leads to frontend
    with token need for reset.

    """

    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.PasswordResetSerializer

    def post(self, request, *args, **kwargs) -> Response:
        """Request password reset.

        Warning: it will always return `Password reset e-mail has been sent.`

        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(
            {"detail": _("Password reset e-mail has been sent.")},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(GenericAPIView):
    """Complete password reset workflow.

    This endpoint confirms the reset of user's password.

    """

    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs) -> Response:
        """Complete password reset."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = serializer.instance
        chamber = getattr(user, "chamber", None)
        return Response(
            {
                "detail": _("Password has been reset with the new password."),
                "subdomain": getattr(chamber, "subdomain", None),
            },
            status=status.HTTP_200_OK,
        )


class SuperAdminLoginView(KnoxLoginView):
    """Super Admin authentication view."""

    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request, *args, **kwargs) -> Response:
        """Login super admin and get auth token with expiry."""
        serializer = serializers.AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        if user.role != UserRole.SUPER_ADMIN.value:
            raise get_invalid_credentials_error()
        login(request, user)
        return super().post(request, format=None)


class ChamberAdminLoginView(KnoxLoginView):
    """Chamber Admin authentication view.

    Successful login will return with Chamber id and Chamber subdomain also.

    """

    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request, *args, **kwargs) -> Response:
        """Login chamber admin, get auth token with chamber id, subdomain."""
        serializer = serializers.NonSAAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get("user")
        if user.role != UserRole.CHAMBER_ADMIN.value:
            raise get_invalid_credentials_error()

        login(request, user)
        return super().post(request, format=None)


class UserRegisterAPIView(KnoxLoginView):
    """Base APIView to register users.

    Inherit from KnoxLoginView to reuse methods to generate auth token.

    """

    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    serializer_class: typing.Type[serializers.UserRegisterSerializer]

    def post(self, request, *args, **kwargs):
        """Complete account creation process, and login the user."""
        serializer = self.serializer_class(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        chamber_admin = serializer.save()
        login(request, chamber_admin)
        return super().post(request, format=None)


class ChamberAdminRegisterAPIView(UserRegisterAPIView):
    """Register API for chamber admins."""

    serializer_class = serializers.ChamberAdminRegisterSerializer


class VolunteerRegisterAPIView(UserRegisterAPIView):
    """Register API for volunteers."""

    serializer_class = serializers.VolunteerRegisterSerializer


class UserRegisterInfoAPIView(GenericAPIView):
    """Base APIView for users to get registration info."""

    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def get(self, request, *args, **kwargs):
        """Return account registration info."""
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )


class ChamberAdminRegisterInfoAPIView(UserRegisterInfoAPIView):
    """API for Chamber admin to get registration info."""

    serializer_class = serializers.ChamberAdminRegisterInfoSerializer


class VolunteerRegisterInfoAPIView(UserRegisterInfoAPIView):
    """API for Volunteer to get registration info."""

    serializer_class = serializers.VolunteerRegisterInfoSerializer


class VolunteerLoginView(KnoxLoginView):
    """Volunteer authentication view.

    Successful login will return with Chamber id and Chamber subdomain.

    """

    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request, *args, **kwargs) -> Response:
        """Login volunteer, get auth token with chamber id and subdomain."""
        serializer = serializers.NonSAAuthTokenSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        if user.role != UserRole.SUPER_ADMIN:
            campaign = Campaign.objects.filter(
                chamber_id=user.chamber_id,
            ).order_by("-id").first()
            user_campaign: UserCampaign = UserCampaign.objects.filter(
                user=user,
                campaign=campaign,
            ).first()
            if user_campaign is None:
                raise get_invalid_credentials_error()
            if user_campaign.deactivated_at:
                raise get_deactivated_user_campaign_error()

        login(request, user)
        return super().post(request, format=None)
