from django.db.models import F, Q

from apps.resources.models import Resource
from apps.users.constants import USER_ROLE_PERMISSIONS_MAP
from apps.users.models.user import User


class ResourceCommonMixin:
    """Provide common functionality for resource view sets."""

    queryset = Resource.objects.annotate(
        category_name=F("category__name"),
    )
    ordering_fields = (
        "category_name",
        "name",
        "file_type",
        "user_group",
    )
    search_fields = ("name",)

    def get_queryset(self):
        """Return only resources that was dedicated to volunteers."""
        qs = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return qs.none()
        user: User = self.request.user
        return qs.filter(
            Q(category__chamber_id=user.chamber_id)
            | Q(category__chamber__isnull=True),
            user_group__overlap=USER_ROLE_PERMISSIONS_MAP.get(
                user.campaign_role,
            ),
        )
