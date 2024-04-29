from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from apps.campaigns.models import UserCampaign
from apps.chambers.models import StoredMember
from apps.core.api.serializers import ModelBaseSerializer
from apps.core.constants import MAX_ZIP_CODE_LENGTH
from apps.users.api.serializers import UserPreferenceSerializer
from apps.users.constants import UserRole

from ...common.serializers.team import TeamSerializer


class ProfileSerializer(ModelBaseSerializer):
    """Serializer for updating profile of volunteer."""

    preference = UserPreferenceSerializer(
        required=False,
        allow_null=True,
        source="user.preference",
    )
    company_zip_code = serializers.CharField(max_length=MAX_ZIP_CODE_LENGTH)
    birthday = serializers.DateField(
        source="user.birthday",
        allow_null=True,
    )
    home_address = serializers.CharField(
        source="user.home_address",
        allow_blank=True,
        max_length=255,
    )
    home_city = serializers.CharField(
        source="user.home_city",
        allow_blank=True,
        max_length=255,
    )
    home_state = serializers.CharField(
        source="user.home_state",
        allow_blank=True,
        max_length=2,
    )
    home_zip_code = serializers.CharField(
        source="user.home_zip_code",
        allow_blank=True,
        max_length=MAX_ZIP_CODE_LENGTH,
    )
    team = TeamSerializer(read_only=True)
    member = serializers.PrimaryKeyRelatedField(
        queryset=StoredMember.objects.all(),
    )
    role = serializers.SerializerMethodField()

    class Meta:
        model = UserCampaign
        fields = (
            "id",
            "user_id",
            "email",
            "first_name",
            "last_name",
            "role",
            "avatar",
            "mobile_phone",
            "work_phone",
            "birthday",
            "home_address",
            "home_city",
            "home_state",
            "home_zip_code",
            "title",
            "company_name",
            "company_address",
            "company_city",
            "company_state",
            "company_zip_code",
            "preferred_contact_methods",
            "preference",
            "team",
            "member",
        )
        read_only_fields = (
            "id",
            "user_id",
            "email",
            "role",
            "avatar",
        )

    def update(self, instance, validated_data):
        """Update user and user preference."""
        user_data = validated_data.pop("user", {})
        preference_data = user_data.pop("preference", {})
        user_campaign = super().update(instance, validated_data)
        for field, value in user_data.items():
            setattr(instance.user, field, value)
        user_campaign.user.save()
        if preference_data is None:
            return user_campaign
        preference_data["user"] = user_campaign.user
        preference_serializer = self.fields["preference"]
        preference_serializer.update(
            user_campaign.user.preference,
            preference_data,
        )
        return user_campaign

    def validate_birthday(self, value):
        """Ensure that birthday is not in the future."""
        if value and value > timezone.now().date():
            raise serializers.ValidationError(
                _("Birthday cannot be in the future."),
            )
        return value

    def get_role(self, user_campaign: UserCampaign) -> str:
        """Return chamber's role instead of campaign role for CA."""
        if user_campaign.user.role == UserRole.CHAMBER_ADMIN:
            return user_campaign.user.role
        return user_campaign.role


class SuperAdminProfileSerializer(ProfileSerializer):
    """Represent super admin profile in VS."""

    role = serializers.CharField()
    preference = UserPreferenceSerializer()
    mobile_phone = serializers.CharField()
    work_phone = serializers.CharField()
    birthday = serializers.DateField()
    home_address = serializers.CharField()
    home_city = serializers.CharField()
    home_state = serializers.CharField()
    home_zip_code = serializers.CharField()
    company_zip_code = serializers.CharField(default="")
    team = TeamSerializer(default=None)
    member = serializers.IntegerField(default=None)
    preferred_contact_methods = serializers.ListField(
        child=serializers.CharField(),
        default=list,
    )

    def create(self, validated_data):
        """Do not allow."""

    def update(self, instance, validated_data):
        """Do not allow."""
