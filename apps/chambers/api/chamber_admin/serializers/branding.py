from drf_spectacular.utils import extend_schema_serializer
from s3direct.api.fields import S3DirectUploadURLField

from apps.core.api.serializers import ModelBaseSerializer

from ....models import ChamberBranding


@extend_schema_serializer(component_name="ChamberBrandingCA")
class ChamberBrandingSerializer(ModelBaseSerializer):
    """Serializer to update branding information for chamber admin."""

    chamber_logo = S3DirectUploadURLField(allow_blank=False, allow_null=True)
    trc_logo = S3DirectUploadURLField(allow_blank=False, allow_null=True)
    landing_bg = S3DirectUploadURLField(allow_blank=False, allow_null=True)

    class Meta:
        model = ChamberBranding
        fields = (
            "site_primary_color",
            "site_secondary_color",
            "site_alternate_color",
            "chamber_logo",
            "trc_logo",
            "landing_bg",
            "headline",
            "public_prelaunch_msg",
            "volunteer_prelaunch_msg",
        )
        extra_kwargs = {
            "public_prelaunch_msg": {"read_only": True},
            "volunteer_prelaunch_msg": {"read_only": True},
        }


class ChamberBrandingPartialUpdateSerializer(ModelBaseSerializer):
    """Serializer to update part of chamber branding information."""

    class Meta:
        model = ChamberBranding
        fields = (
            "public_prelaunch_msg",
            "volunteer_prelaunch_msg",
        )
