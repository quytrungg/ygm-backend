from drf_spectacular.utils import extend_schema_serializer
from s3direct.api.fields import S3DirectUploadURLField

from apps.chambers.models import ChamberBranding
from apps.core.api.serializers import ModelBaseSerializer


class ChamberBrandingUpdateSerializer(ModelBaseSerializer):
    """Serializer for updating ChamberBranding model."""

    chamber_logo = S3DirectUploadURLField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ChamberBranding
        fields = (
            "chamber_logo",
        )


@extend_schema_serializer(component_name="ChamberBrandingSA")
class ChamberBrandingSerializer(ModelBaseSerializer):
    """Serializer for ChamberBranding model."""

    chamber_logo = S3DirectUploadURLField(
        required=False,
        allow_null=True,
    )
    trc_logo = S3DirectUploadURLField(
        required=False,
        allow_null=True,
    )
    landing_bg = S3DirectUploadURLField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ChamberBranding
        fields = (
            "site_primary_color",
            "site_secondary_color",
            "site_alternate_color",
            "headline",
            "public_prelaunch_msg",
            "volunteer_prelaunch_msg",
            "chamber_logo",
            "trc_logo",
            "landing_bg",
        )
        extra_kwargs = {
            "site_primary_color": {"required": False, "allow_blank": True},
            "site_secondary_color": {"required": False, "allow_blank": True},
            "site_alternate_color": {"required": False, "allow_blank": True},
            "headline": {"required": False, "allow_blank": True},
            "public_prelaunch_msg": {
                "required": False,
                "allow_blank": True,
            },
            "volunteer_prelaunch_msg": {
                "required": False,
                "allow_blank": True,
            },
        }
