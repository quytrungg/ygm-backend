from rest_framework import mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from libs.open_api.extend_schema import (
    CAAutoSchema,
    PSAutoSchema,
    VSAutoSchema,
)

from apps.campaigns import models as campaigns_models
from apps.chambers.models import Chamber

from ...campaigns.services import get_chamber_newest_campaign
from ...users.constants import UserRole
from . import mixins as core_mixins
from .permissions import (
    AllowAdmin,
    AllowAllRoles,
    AllowChamberAdmin,
    IsCampaignInProgress,
)
from .serializers import CampaignPublicSerializer


class BaseViewSet(
    core_mixins.ActionPermissionsMixin,
    core_mixins.ActionSerializerMixin,
    GenericViewSet,
):
    """Base viewset for api."""

    base_permission_classes = (IsAuthenticated,)

    def get_viewset_permissions(self):
        """Prepare viewset permissions.

        Method returns union of `base_permission_classes` and
        `permission_classes`, specified in child classes.

        """
        extra_permissions = tuple(
            permission for permission in self.permission_classes
            if permission not in self.base_permission_classes
        )
        permissions = self.base_permission_classes + extra_permissions
        return [permission() for permission in permissions]


class CRUDViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    core_mixins.UpdateModelWithoutPatchMixin,
    mixins.DestroyModelMixin,
    BaseViewSet,
):
    """CRUD viewset for api views."""


class ReadOnlyViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    """Read only viewset for api views."""


class AdminBaseViewSet(BaseViewSet):
    """Base view for Admin base Views."""

    permissions_map = {
        "default": (AllowAdmin,),
    }


class ChamberAPIViewMixin:
    """Mixin for Chamber APIs."""

    schema = CAAutoSchema()

    def perform_authentication(self, request):
        """Perform authentication on the incoming request.

        Also attach the selected `campaign` of current user's chamber on the
        `request`.

        """
        super().perform_authentication(request)
        request.campaign = self.get_current_selected_campaign(request)

    def get_current_selected_campaign(
        self,
        request,
    ) -> campaigns_models.Campaign | None:
        """Return the currently selected campaign."""
        if not request.user.is_authenticated:
            return None

        campaign_id = self.get_selected_campaign_id(request)
        if not campaign_id:
            return None
        return campaigns_models.Campaign.objects.filter(
            id=campaign_id,
            chamber_id=request.user.chamber_id,
        ).first()

    def get_selected_campaign_id(self, request):
        """Return the currently selected campaign's id."""
        return str(request.META.get("HTTP_CAMPAIGN", ""))


class ChamberBaseViewSet(ChamberAPIViewMixin, BaseViewSet):
    """Base view for Chamber base Views."""

    permissions_map = {
        "default": (AllowChamberAdmin,),
    }


class VolunteerBaseViewSet(BaseViewSet):
    """Base view for Volunteer base Views."""

    permissions_map = {
        "default": (AllowAllRoles, IsCampaignInProgress),
    }
    schema = VSAutoSchema()

    def perform_authentication(self, request):
        """Perform authentication on the incoming request.

        Also attach the latest `campaign` of current accessed chamber
        on the `request`.

        """
        super().perform_authentication(request)
        request.campaign = self._get_campaign(request)

    def _get_campaign(
        self,
        request,
    ) -> campaigns_models.Campaign | None:
        """Return the current accessed chamber's campaign."""
        if not request.user.is_authenticated:
            return None

        if not self.is_user_super_admin:
            return get_chamber_newest_campaign(chamber=request.user.chamber)

        chamber = self._get_current_accessed_chamber(request)
        if not chamber:
            return None
        return get_chamber_newest_campaign(chamber=chamber)

    def _get_current_accessed_chamber(self, request):
        """Return the current accessed chamber's id."""
        chamber_id = str(request.query_params.get("chamber", ""))
        if not chamber_id or not chamber_id.isdigit():
            return None
        return Chamber.objects.filter(id=chamber_id).first()

    @property
    def is_user_super_admin(self) -> bool:
        """Check if current user is SA."""
        return getattr(self.request.user, "role", None) == UserRole.SUPER_ADMIN


class PublicBaseViewSet(BaseViewSet):
    """Base view for public APIs."""

    base_permission_classes = (AllowAny,)
    authentication_classes = ()
    schema = PSAutoSchema()

    def perform_authentication(self, request):
        """Attach an in-progress `campaign` instance of request's chamber."""
        serializer = CampaignPublicSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=False)
        campaign = serializer.validated_data.get("campaign")
        request.campaign = campaign
