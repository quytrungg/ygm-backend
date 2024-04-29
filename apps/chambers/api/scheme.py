from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)

from .. import resources
from .chamber_admin import views as ca_views
from .public import views as public_views
from .super_admin import views as sa_views
from .super_admin.serializers import ChamberStatisticsSerializer

extend_schema_view(
    nickname_unique=extend_schema(
        parameters=[
            OpenApiParameter(
                name="nickname",
                description="Chamber Nickname",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        "Chamber Nickname",
                        summary=(
                            "Check if chamber nickname is unique."
                        ),
                        value="string",
                    ),
                ],
            ),
        ],
    ),
    get_statistics=extend_schema(
        parameters=[
            OpenApiParameter(
                name="year",
                description="Year of the statistics",
                required=False,
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample(
                        name="Year 2020",
                        value=2020,
                    ),
                ],
            ),
        ],
        responses={
            200: ChamberStatisticsSerializer(many=True),
        },
    ),
)(sa_views.ChamberViewSet)

extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name="subdomain",
                description="Subdomain",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
    ),
)(public_views.ChamberSubdomainValidateAPIView)

extend_schema_view(
    get_import_template=extend_schema(
        parameters=[
            OpenApiParameter(
                name="file_format",
                description="Available file formats",
                required=True,
                enum=resources.SUPPORTED_FORMATS_MAP.keys(),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses=OpenApiTypes.BINARY,
    ),
)(ca_views.StoredMemberImportViewSet)
