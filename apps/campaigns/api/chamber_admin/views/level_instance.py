from django.utils.translation import gettext_lazy as _

from rest_framework import response, status
from rest_framework.decorators import action

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.permissions import (
    AllowChamberAdmin,
    IsCampaignLive,
    IsCampaignRenewal,
)
from apps.core.api.views import ChamberBaseViewSet

from ....models import LevelInstance
from ...permissions import IsLevelInstanceEditable
from .. import serializers


class LevelInstanceViewSet(
    UpdateModelWithoutPatchMixin,
    ChamberBaseViewSet,
):
    """Viewset for chamber admin to manage LevelInstance."""

    queryset = LevelInstance.objects.all().select_related("contract", "level")
    serializer_class = serializers.LevelInstanceSerializer
    serializers_map = {
        "update": serializers.LevelInstanceUpdateSerializer,
    }
    permissions_map = {
        "default": (
            AllowChamberAdmin,
            IsCampaignRenewal | IsCampaignLive,
            IsLevelInstanceEditable,
        ),
    }

    @action(detail=True, methods=("post",))
    def decline(self, *args, **kwargs):
        """Mark selected level instance declined and update contract status."""
        level_instance = self.get_object()
        if not level_instance.contract:
            return response.Response(
                data={"error": _("Cannot decline instance with no contract")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        level_instance.decline()
        new_level = LevelInstance(
            level=level_instance.level,
            contract=None,
            cost=level_instance.level.cost,
            declined_at=None,
        )
        new_level.save()
        contract = level_instance.contract
        if contract.levels.filter(declined_at__isnull=True).count() == 0:
            contract.decline()
        return response.Response(status=status.HTTP_200_OK)

    def get_queryset(self):
        """Get contract of all level instances within current campaign."""
        qs = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return qs.none()
        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()

        return qs.filter(
            level__product__category__campaign_id=campaign.pk,
        )
