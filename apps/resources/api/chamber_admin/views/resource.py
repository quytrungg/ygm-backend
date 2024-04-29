from rest_framework import mixins

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.views import ChamberBaseViewSet

from ...common.views.resource import ResourceCommonMixin
from ..serializers import ResourceSerializer


class ResourceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    UpdateModelWithoutPatchMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    ResourceCommonMixin,
    ChamberBaseViewSet,
):
    """View for Chamber Resource Management."""

    serializer_class = ResourceSerializer

    def check_object_permissions(self, request, obj):
        """Restrict CA access to modify SA resources."""
        super().check_object_permissions(request, obj)
        if self.action in ("destroy", "partial_update", "update"):
            if obj.category.chamber_id != request.user.chamber_id:
                self.permission_denied(
                    request,
                    message=(
                        "This resource was shared with you by YGM. "
                        "You cannot edit this resource.",
                    ),
                )
