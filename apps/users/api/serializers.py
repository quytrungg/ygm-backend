from rest_framework import serializers

from s3direct.api.fields import S3DirectUploadURLField

from apps.core.api.serializers import ModelBaseSerializer
from apps.users.models import User, UserPreference


class UserSerializer(ModelBaseSerializer):
    """Serializer for representing `User`."""

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "role",
            "avatar",
            "last_login",
            "created",
            "modified",
        )
        read_only_fields = (
            "email",
            "last_login",
            "created",
            "modified",
        )


class UserProfileSerializer(ModelBaseSerializer):
    """Serializer for user basic information."""

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
        )


class UserPreferenceSerializer(ModelBaseSerializer):
    """Serializer for representing `UserPreference`."""

    class Meta:
        model = UserPreference
        fields = (
            "favorite_candy",
            "favorite_drink",
            "favorite_restaurant",
            "favorite_movie",
            "hobbies",
            "instagram_url",
            "facebook_url",
            "twitter_url",
            "linkedin_url",
        )


class ProfileSASerializer(ModelBaseSerializer):
    """Serializer for updating profile of super admin."""

    avatar = S3DirectUploadURLField(required=False, allow_null=True)
    preference = UserPreferenceSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "mobile_phone",
            "home_phone",
            "fax",
            "avatar",
            "title",
            "company",
            "role",
            "address",
            "preference",
        )
        read_only_fields = (
            "id",
            "email",
            "role",
        )

    def update(self, instance, validated_data):
        """Update user and user preference."""
        preference = validated_data.pop("preference", None)
        user = super().update(instance, validated_data)
        if preference is None:
            return user

        preference["user"] = user
        preference_serializer = self.fields["preference"]
        preference_serializer.update(user.preference, preference)
        return user


class ProfileCASerializer(ModelBaseSerializer):
    """Serializer for updating profile of chamber admin."""

    avatar = S3DirectUploadURLField(required=False, allow_null=True)
    preference = UserPreferenceSerializer(required=False, allow_null=True)
    chamber_subdomain = serializers.CharField(
        source="chamber.subdomain",
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "mobile_phone",
            "home_phone",
            "fax",
            "avatar",
            "title",
            "company",
            "role",
            "address",
            "preference",
            "chamber_id",
            "chamber_subdomain",
        )
        read_only_fields = (
            "id",
            "email",
            "role",
            "chamber_id",
        )

    def update(self, instance, validated_data):
        """Update user and user preference."""
        preference = validated_data.pop("preference", None)
        user = super().update(instance, validated_data)
        if preference is None:
            return user

        preference["user"] = user
        preference_serializer = self.fields["preference"]
        preference_serializer.update(user.preference, preference)
        return user
