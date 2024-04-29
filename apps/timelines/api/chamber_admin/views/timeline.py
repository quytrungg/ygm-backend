from rest_framework import mixins, response
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.permissions import AllowChamberAdmin
from apps.core.api.views import ChamberBaseViewSet

from ....models import Timeline
from ....permissions import IsTimelineIncomplete
from .. import serializers


class TimelineViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    UpdateModelWithoutPatchMixin,
    ChamberBaseViewSet,
):
    """Provide APIs to manage Timeline."""

    queryset = Timeline.objects.all().order_by("order").select_related(
        "created_by",
    ).prefetch_related("attachments")
    serializer_class = serializers.TimelineSerializer
    ordering_fields = (
        "name",
        "category__name",
    )
    serializers_map = {
        "reorder": serializers.TimelineReorderSerializer,
        "default": serializers.TimelineSerializer,
    }
    search_fields = (
        "name",
        "status",
        "due_date",
        "created_by__email",
        "assigned_to",
        "category__name",
    )
    permissions_map = {
        "update": (AllowChamberAdmin, IsTimelineIncomplete),
        "default": (AllowChamberAdmin,),
    }

    def get_queryset(self):
        """Return Timeline queryset of current user's chamber."""
        if getattr(self, "swagger_fake_view", False):
            return self.queryset.none()
        qs = super().get_queryset().filter(
            chamber_id=self.request.user.chamber_id,
        )
        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs
        return qs.filter(type_id=campaign.timeline_id)

    # pylint: disable=unused-argument
    @extend_schema(request=None, responses=None)
    @action(methods=("put",), detail=True)
    def complete(self, request, *args, **kwargs):
        """Complete the timeline, change `status` to `COMPLETED`."""
        timeline = self.get_object()
        timeline.mark_completed()
        return response.Response()

    @action(methods=("put",), detail=True)
    def reorder(self, request, *args, **kwargs) -> response.Response:
        """Reorder items in timeline list."""
        timeline = self.get_object()
        serializer = self.get_serializer(timeline, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response()
