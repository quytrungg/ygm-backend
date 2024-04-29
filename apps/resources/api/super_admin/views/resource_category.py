from rest_framework import mixins

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.views import AdminBaseViewSet

from ....models import ResourceCategory
from ..serializers import ResourceCategorySerializer


class ResourceCategoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    UpdateModelWithoutPatchMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    AdminBaseViewSet,
):
    """Provide Resource category management for Super Admin."""

    queryset = ResourceCategory.objects.all()
    serializer_class = ResourceCategorySerializer
    ordering_fields = (
        "name",
        "chamber",
    )
    search_fields = (
        "name",
    )
