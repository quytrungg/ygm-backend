from rest_framework import mixins

from apps.core.api.views import ChamberBaseViewSet

from ....models import ChamberBranding
from .. import serializers


class ChamberBrandingViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    ChamberBaseViewSet,
):
    """Viewset for chamber admin to manage chamber branding."""

    queryset = ChamberBranding.objects.all()
    serializer_class = serializers.ChamberBrandingSerializer
    ordering_fields = ()
    search_fields = ()
    serializers_map = {
        "partial_update": serializers.ChamberBrandingPartialUpdateSerializer,
        "default": serializers.ChamberBrandingSerializer,
    }

    def get_object(self) -> ChamberBranding:
        """Return the corresponding chamber branding for the chamber admin."""
        return ChamberBranding.objects.filter(
            chamber_id=self.request.user.chamber_id,
        ).first()
