from django.db.models import F

from rest_framework import mixins

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.views import AdminBaseViewSet

from ....models import Resource
from ..serializers import ResourceSerializer


class ResourceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    UpdateModelWithoutPatchMixin,
    mixins.DestroyModelMixin,
    AdminBaseViewSet,
):
    """Provide Resource management for Super Admin."""

    queryset = Resource.objects.annotate(
        category_name=F("category__name"),
    )
    serializer_class = ResourceSerializer
    ordering_fields = (
        "category_name",
        "name",
        "file_type",
        "user_group",
    )
    filterset_fields = (
        "category__chamber",
        "category",
    )
    search_fields = (
        "name",
    )
