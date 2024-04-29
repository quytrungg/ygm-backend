from django.conf import settings
from django.contrib.auth import (
    authenticate,
    get_user_model,
    password_validation,
)
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.utils.encoding import DjangoUnicodeDecodeError, force_str
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from libs.open_api.serializers import OpenApiSerializer

from apps.campaigns.constants import CAMPAIGN_IN_PROGRESS_STATUSES
from apps.core.api.serializers import ModelBaseSerializer
from apps.core.exceptions import NonFieldValidationError

from ... import services
from ..serializers import UserSerializer

User = get_user_model()


def get_invalid_credentials_error() -> NonFieldValidationError:
    """Return Validation error for invalid credentials."""
    msg = _("Unable to log in with provided credentials.")
    return NonFieldValidationError(msg)


def get_deactivated_user_campaign_error() -> NonFieldValidationError:
    """Return Validation error for deactivated user campaign."""
    msg = _("Your account is inactive. Please contact your campaign admin.")
    return NonFieldValidationError(msg)


class AuthTokenSerializer(serializers.Serializer):
    """Custom auth serializer to use email instead of username.

    Copied form rest_framework.authtoken.serializers.AuthTokenSerializer

    """

    email = serializers.CharField(
        write_only=True,
        required=True,
    )
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
        required=True,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        # The authenticate call simply returns None for is_active=False
        # users. (Assuming the default ModelBackend authentication
        # backend.)
        if not user:
            raise get_invalid_credentials_error()

        attrs["user"] = user
        return attrs

    def create(self, validated_data: dict):
        """Escape warning."""

    def update(self, instance, validated_data):
        """Escape warning."""


class TokenSerializer(OpenApiSerializer):
    """Auth token for entire app."""

    expiry = serializers.IntegerField(
        help_text=f"Token expires in {settings.REST_KNOX['TOKEN_TTL']}",
    )
    token = serializers.CharField(help_text="Token itself")
    user = UserSerializer()


class PasswordResetSerializer(serializers.Serializer):
    """Request for resetting user's password."""

    email = serializers.EmailField(
        help_text="Email of account which password should be reset",
    )
    chamber_id = serializers.IntegerField(
        help_text="Chamber id if tried to reset from chamber related page",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user: User = None

    def validate(self, attrs):
        """Check that we have user with input email."""
        email = attrs.get("email")
        chamber_id = attrs.get("chamber_id")
        query = User.objects.filter(email=email)
        if not query.exists():
            raise ValidationError(
                {"email": _("There is no user with such email")},
            )
        user = query.first()
        if chamber_id is not None and (user.chamber_id != chamber_id):
            raise ValidationError(
                {"email": _("There is no user with such email")},
            )
        self._user = user

        return attrs

    def create(self, validated_data: dict):
        return services.reset_user_password(self._user)

    def update(self, instance, validated_data):
        """Escape warning."""


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Request for resetting user's password.

    Explanation of token and uid

    Example `MQ-5b2-e2c1ce64d63673f0e78f`, where `MQ` - is `uid` or user id and
    `5b2-e2c1ce64d63673f0e78f` - `token` for resetting password

    """

    password = serializers.CharField(
        max_length=128,
    )
    password_confirm = serializers.CharField(
        max_length=128,
    )
    uid = serializers.CharField()
    token = serializers.CharField()
    _token_generator = PasswordResetTokenGenerator()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user: User = None

    def validate_uid(self, uid: str) -> str:
        """Validate that uid can be decoded and it's valid."""
        try:
            user_pk = force_str(urlsafe_base64_decode(uid))
        except DjangoUnicodeDecodeError as error:
            raise ValidationError(_("Invalid uid")) from error
        query = User.objects.filter(pk=user_pk)
        if not query.exists():
            raise ValidationError(_("Invalid uid"))
        self._user = query.first()
        return uid

    def validate_token(self, token: str) -> str:
        """Validate token."""
        if not self._token_generator.check_token(self._user, token):
            raise ValidationError(_("Invalid token"))
        return token

    def validate(self, attrs):
        """Validate passwords."""
        password = attrs["password"]
        password_confirm = attrs["password_confirm"]
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError(
                    {
                        "password_confirm": _("Passwords mismatch"),
                    },
                )
        password_validation.validate_password(password, self._user)
        return attrs

    def create(self, validated_data: dict) -> User:
        password = self.validated_data["password"]
        self._user.set_password(password)
        self._user.save()
        return self._user

    def update(self, instance, validated_data):
        """Escape warning."""


class UserRegisterTokenMixin(ModelBaseSerializer):
    """Provide common fields and validation for chamber admin registration."""

    uid = serializers.CharField(required=True, write_only=True)
    token = serializers.CharField(required=True, write_only=True)
    chamber_id = serializers.IntegerField(required=True)
    _token_generator = PasswordResetTokenGenerator()

    def get_queryset(self):
        """Return queryset to get registering user."""
        return User.objects.filter(last_login__isnull=True)

    def validate(self, attrs: dict) -> dict:
        """Validate `uid` and `token`."""
        attrs = super().validate(attrs)
        uid = attrs["uid"]
        errors = {}
        try:
            user_pk = force_str(urlsafe_base64_decode(uid))
        except (DjangoUnicodeDecodeError, ValueError) as exc:
            raise serializers.ValidationError(
                {"uid": _("Invalid uid.")},
            ) from exc
        user = self.get_queryset().filter(pk=user_pk).first()
        if not user:
            errors["uid"] = _("Invalid uid")
        self._user = user
        if not self._token_generator.check_token(self._user, attrs["token"]):
            errors["token"] = _("Invalid token")
        if errors:
            raise serializers.ValidationError(errors)
        if self._user.chamber_id != attrs["chamber_id"]:
            raise serializers.ValidationError(_("Invalid credentials."))
        return attrs


class UserRegisterSerializer(
    UserRegisterTokenMixin,
    ModelBaseSerializer,
):
    """Serializer for user to register account."""

    password = serializers.CharField(required=True, write_only=True)
    password_confirm = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            "password",
            "password_confirm",
            "uid",
            "token",
            "chamber_id",
        )

    def validate(self, attrs: dict) -> dict:
        """Validate 2 passwords match."""
        attrs = super().validate(attrs)
        password = attrs["password"]
        password_confirm = attrs.pop("password_confirm")
        if password != password_confirm:
            raise ValidationError(
                {
                    "password_confirm": _("Passwords mismatch"),
                },
            )
        try:
            password_validation.validate_password(
                password,
                self._user,
            )
        except ValidationError as exc:
            raise ValidationError({"password": exc.messages}) from exc
        return attrs

    def save(self, **kwargs):
        """Set password for user."""
        password = self.validated_data.pop("password")
        user = self._user
        user.set_password(password)
        user.save()
        return user


class ChamberAdminRegisterSerializer(UserRegisterSerializer):
    """Serializer for chamber admin to register account."""

    def get_queryset(self):
        """Return chamber admin users only."""
        return super().get_queryset().filter(role=User.ROLES.CHAMBER_ADMIN)


class VolunteerRegisterSerializer(UserRegisterSerializer):
    """Serializer for volunteer to register account."""

    def get_queryset(self):
        """Return volunteer users of in-progress campaigns only."""
        return User.objects.filter(
            role=User.ROLES.VOLUNTEER,
            user_campaigns__campaign__status__in=CAMPAIGN_IN_PROGRESS_STATUSES,
        )


class UserRegisterInfoSerializer(
    UserRegisterTokenMixin,
    ModelBaseSerializer,
):
    """Serializer for users to get registration info."""

    class Meta:
        model = User
        read_only_fields = (
            "first_name",
            "last_name",
            "email",
        )
        fields = (
            "uid",
            "token",
            "chamber_id",
        ) + read_only_fields

    def to_representation(self, instance: User) -> dict:
        """Return data of registering user."""
        return super().to_representation(self._user)


class ChamberAdminRegisterInfoSerializer(UserRegisterInfoSerializer):
    """Serializer for chamber admins to get registration info."""

    class Meta(UserRegisterInfoSerializer.Meta):
        fields = UserRegisterInfoSerializer.Meta.fields + ("mobile_phone",)

    def get_queryset(self):
        """Filter chamber admin users only."""
        return super().get_queryset().filter(role=User.ROLES.CHAMBER_ADMIN)


class VolunteerRegisterInfoSerializer(UserRegisterInfoSerializer):
    """Serializer for volunteers to get registration info."""

    def get_queryset(self):
        """Filter volunteer users of in-progress campaigns only."""
        return super().get_queryset().filter(
            role=User.ROLES.VOLUNTEER,
            user_campaigns__campaign__status__in=CAMPAIGN_IN_PROGRESS_STATUSES,
        )


class NonSAAuthTokenSerializer(AuthTokenSerializer):
    """Provide process login flow of CA/VS site."""

    chamber_id = serializers.IntegerField()

    def validate(self, attrs):
        """Check if user's chamber matches chamber's site from request."""
        attrs = super().validate(attrs)
        user = attrs.get("user")
        chamber_id = attrs.get("chamber_id")
        if user.role == User.ROLES.SUPER_ADMIN:
            return attrs

        if not chamber_id or chamber_id != user.chamber_id:
            raise get_invalid_credentials_error()

        return attrs
