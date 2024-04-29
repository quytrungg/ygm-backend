from rest_framework import mixins

from apps.core.api.views import VolunteerBaseViewSet

from ...common.views.resource import ResourceCommonMixin
from ..serializers import ResourceSerializer


class ResourceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    ResourceCommonMixin,
    VolunteerBaseViewSet,
):
    """Provide view for Volunteer Resource."""

    serializer_class = ResourceSerializer
