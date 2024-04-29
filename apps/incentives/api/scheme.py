from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)

from .chamber_admin import views
from .chamber_admin.serializers import (
    QualifierAmountListSerializer,
    QualifierNameListSerializer,
    RewardAccumulatingLevelSerializer,
    RewardMarkPaymentStatusSerializer,
)

extend_schema_view(
    get_qualifier_amounts=extend_schema(
        responses={
            200: QualifierAmountListSerializer(many=True),
        },
    ),
    get_qualifier_names=extend_schema(
        responses={
            200: QualifierNameListSerializer(many=True),
        },
    ),
)(views.IncentiveViewSet)

extend_schema_view(
    put=extend_schema(
        request=RewardMarkPaymentStatusSerializer(many=True),
    ),
)(views.RewardMarkPaymentStatusAPIView)

extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="session_start",
                description="Session start",
                required=True,
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="session_end",
                description="Session end",
                required=True,
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
            ),
        ],
    ),
)(views.RallySessionViewSet)


extend_schema_view(
    accumulating_levels=extend_schema(
        responses=RewardAccumulatingLevelSerializer(many=True),
    ),
)(views.RewardViewSet)
