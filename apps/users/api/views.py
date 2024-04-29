from django.contrib.auth import get_user_model

from rest_framework import mixins

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.views import AdminBaseViewSet, ChamberBaseViewSet

from . import serializers

User = get_user_model()


class ProfileSAViewSet(
    mixins.RetrieveModelMixin,
    UpdateModelWithoutPatchMixin,
    AdminBaseViewSet,
):
    """Viewset for viewing and editing super admin's profile."""

    queryset = User.objects.all()
    serializer_class = serializers.ProfileSASerializer
    search_fields = (
        "first_name",
        "last_name",
    )

    def get_object(self):
        """Return the current user."""
        return self.request.user


class ProfileCAViewSet(
    mixins.RetrieveModelMixin,
    UpdateModelWithoutPatchMixin,
    ChamberBaseViewSet,
):
    """Viewset for viewing and editing chamber admin's profile."""

    queryset = User.objects.all().select_related("chamber")
    serializer_class = serializers.ProfileCASerializer
    search_fields = (
        "first_name",
        "last_name",
    )

    def get_object(self):
        """Return the current user."""
        return self.request.user
