import typing

from rest_framework.views import APIView

from drf_spectacular.utils import OpenApiParameter
from drf_standardized_errors.openapi import AutoSchema

from libs.open_api.view_fixers import ApiViewFix


def fix_api_view_warning(class_to_fix: typing.Type[APIView]):
    """Fix warning `This is graceful fallback handling for APIViews`."""

    class FixedApiView(ApiViewFix):
        """Generated fixed class."""

        target_class = f"{class_to_fix.__module__}.{class_to_fix.__name__}"

    return FixedApiView


class CAAutoSchema(AutoSchema):
    """Schema class for CA APIs."""

    global_params = [
        OpenApiParameter(
            name="chamber",
            type=int,
            location=OpenApiParameter.HEADER,
            description="Chamber id for impersonation",
        ),
        OpenApiParameter(
            name="campaign",
            type=int,
            location=OpenApiParameter.HEADER,
            description="Currently selected campaign's id",
            required=True,
        ),
    ]

    def get_override_parameters(self):
        """Append custom params to schema parameters."""
        params = super().get_override_parameters()
        return params + self.global_params


class VSAutoSchema(AutoSchema):
    """Schema class for VS APIs."""

    global_params = [
        OpenApiParameter(
            name="chamber",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Chamber ID",
        ),
    ]

    def get_override_parameters(self):
        """Append custom params to schema parameters."""
        params = super().get_override_parameters()
        return params + self.global_params


class PSAutoSchema(AutoSchema):
    """Schema class for PS APIs."""

    global_params = [
        OpenApiParameter(
            name="chamber",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Chamber ID",
        ),
    ]

    def get_override_parameters(self):
        """Append custom params to schema parameters."""
        params = super().get_override_parameters()
        return params + self.global_params
