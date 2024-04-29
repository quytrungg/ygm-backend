from rest_framework import mixins

from apps.core.api.permissions import AllowAllRoles
from apps.core.api.views import VolunteerBaseViewSet

from ....models import StoredMember
from ...common.serializers import StoredMemberSerializer


class StoredMemberViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    VolunteerBaseViewSet,
):
    """Provide access to Stored Members for volunteers."""

    queryset = StoredMember.objects.all()
    serializer_class = StoredMemberSerializer
    permissions_map = {
        "default": (AllowAllRoles,),
    }
    ordering_fields = (
        "name",
    )
    search_fields = (
        "name",
        "contact_first_name",
        "contact_last_name",
        "contact_email",
        "address",
    )

    def get_queryset(self):
        """Return only members within the chamber."""
        if getattr(self, "swagger_fake_view", False):
            return self.queryset.none()
        qs = super().get_queryset()
        if self.is_user_super_admin:
            return qs.filter(chamber_id=self.request.campaign.chamber_id)
        return qs.filter(chamber_id=self.request.user.chamber_id)
