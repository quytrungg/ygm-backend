from rest_framework import serializers

from s3direct.api.fields import S3DirectUploadURLField

from apps.core.api.serializers import ModelBaseSerializer

from ....models import Team, UserCampaign


class UserCampaignSerializer(ModelBaseSerializer):
    """Serializer for users involved in a campaign."""

    team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
    )
    avatar = S3DirectUploadURLField(allow_blank=False, allow_null=True)

    class Meta:
        model = UserCampaign
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "role",
            "company_name",
            "campaign",
            "team",
            "user",
            "avatar",
            "is_active",
        )


class UserCampaignCompactSerializer(ModelBaseSerializer):
    """Represent compact information of UserCampaign."""

    member_name = serializers.CharField(default="", read_only=True)
    contract_count = serializers.CharField(default="", read_only=True)

    class Meta:
        model = UserCampaign
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "role",
            "team",
            "company_name",
            "is_active",
            "avatar",
            "member_name",
            "contract_count",
            "member",
            "deactivated_at",
        )
