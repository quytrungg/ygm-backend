from rest_framework import serializers

from libs.open_api.serializers import OpenApiSerializer

from apps.campaigns.models import Campaign
from apps.campaigns.services import get_chamber_newest_campaign
from apps.core.api.serializers import ModelBaseSerializer

from ....models import Chamber
from .branding import ChamberBrandingSerializer


class LatestCampaignSerializer(ModelBaseSerializer):
    """Represent information of latest campaign in public API."""

    class Meta:
        model = Campaign
        fields = (
            "id",
            "name",
            "status",
            "is_renewed",
            "year",
            "goal",
            "has_trades",
        )


class ChamberSerializer(ModelBaseSerializer):
    """Serializer of Chamber profile."""

    branding = ChamberBrandingSerializer()

    class Meta:
        model = Chamber
        fields = (
            "id",
            "name",
            "subdomain",
            "trc_coord_email",
            "ceo_email",
            "address",
            "city",
            "state",
            "zipcode",
            "country",
            "mail_address",
            "phone",
            "instagram_url",
            "facebook_url",
            "twitter_url",
            "youtube_url",
            "linkedin_url",
            "branding",
        )


class ChamberSubdomainValidateSerializer(OpenApiSerializer):
    """Represent serializer to validate subdomain for volunteer site."""

    subdomain = serializers.CharField(write_only=True)
    chamber = ChamberSerializer(read_only=True)
    campaign = LatestCampaignSerializer(read_only=True)

    class Meta:
        fields = (
            "subdomain",
            "chamber",
            "campaign",
        )

    def validate(self, attrs):
        """Validate chamber with given subdomain."""
        attrs = super().validate(attrs)
        subdomain = attrs["subdomain"]
        chamber = Chamber.objects.filter(
            subdomain__iexact=subdomain,
        ).select_related("branding").first()
        attrs["chamber"] = chamber
        if not chamber:
            return attrs
        attrs["campaign"] = get_chamber_newest_campaign(chamber)
        return attrs
