from rest_framework import mixins

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.permissions import AllowChamberAdmin, IsCampaignInProgress
from apps.core.api.views import ChamberBaseViewSet

from ....models import Note
from .. import serializers


class NoteViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    UpdateModelWithoutPatchMixin,
    ChamberBaseViewSet,
):
    """View set for Note management."""

    queryset = Note.objects.all().order_by("id")
    serializer_class = serializers.NoteSerializer
    permissions_map = {
        "default": (AllowChamberAdmin, IsCampaignInProgress),
        "list": (AllowChamberAdmin,),
        "retrieve": (AllowChamberAdmin,),
    }
    ordering_fields = ()
    filterset_fields = ("campaign",)
    search_fields = ("type",)

    def get_queryset(self):
        """Filter notes by current campaign."""
        qs = super().get_queryset()
        campaign = getattr(self.request, "campaign", None)
        if getattr(self, "swagger_fake_view", False):
            return qs.none()
        if not campaign:
            return qs.none()
        return qs.filter(campaign=campaign)
