from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)

from .chamber_admin import views as ca_views
from .volunteer import views as vs_views

revenue_from_param = OpenApiParameter(
    name="revenue_from",
    description="Calculate revenue from",
    required=True,
    type=OpenApiTypes.DATETIME,
    location=OpenApiParameter.QUERY,
)
revenue_to_param = OpenApiParameter(
    name="revenue_to",
    description="Calculate revenue to",
    required=True,
    type=OpenApiTypes.DATETIME,
    location=OpenApiParameter.QUERY,
)

extend_schema_view(
    list=extend_schema(
        parameters=[revenue_from_param, revenue_to_param],
    ),
)(vs_views.LeadershipStandingViewSet)


extend_schema_view(
    list=extend_schema(
        parameters=[revenue_from_param, revenue_to_param],
    ),
)(vs_views.TeamStandingViewSet)


extend_schema_view(
    list=extend_schema(
        parameters=[revenue_from_param, revenue_to_param],
    ),
)(vs_views.VolunteerStandingViewSet)


extend_schema_view(
    list=extend_schema(
        parameters=[revenue_from_param, revenue_to_param],
    ),
)(ca_views.LeadershipStandingViewSet)


extend_schema_view(
    list=extend_schema(
        parameters=[revenue_from_param, revenue_to_param],
    ),
)(ca_views.TeamStandingViewSet)


extend_schema_view(
    list=extend_schema(
        parameters=[revenue_from_param, revenue_to_param],
    ),
)(ca_views.VolunteerStandingViewSet)
