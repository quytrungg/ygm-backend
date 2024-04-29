from rest_framework import mixins

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.views import ChamberBaseViewSet

from ....models import ResourceCategory
from ..serializers import ResourceCategorySerializer


class ResourceCategoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    UpdateModelWithoutPatchMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    ChamberBaseViewSet,
):
    """Provide Resource category management for Chamber Admin."""

    queryset = ResourceCategory.objects.all()
    serializer_class = ResourceCategorySerializer
    ordering_fields = (
        "name",
    )
    search_fields = (
        "name",
    )

    def get_queryset(self):
        """Filter only chamber related resources."""
        qs = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return qs.none()
        return qs.filter(
            chamber_id=self.request.user.chamber_id,
        )
