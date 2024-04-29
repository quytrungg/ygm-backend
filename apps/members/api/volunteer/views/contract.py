from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework import mixins, response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.campaigns.models import LevelInstance, UserCampaign
from apps.core.api import mixins as core_mixins
from apps.core.api import views
from apps.core.api.permissions import (
    AllowAllRoles,
    IsCampaignLive,
    IsCampaignRenewal,
    IsChamberChair,
    IsVolunteer,
)
from apps.members import services
from apps.members.models import Contract

from ...common.serializers import ContractPublicDetailSerializer
from ...filters import ContractFilter
from ...permissions import IsDraftContract
from .. import serializers


class ContractViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    core_mixins.UpdateModelWithoutPatchMixin,
    mixins.DestroyModelMixin,
    views.VolunteerBaseViewSet,
):
    """Provide APIs for volunteer to manage contracts."""

    # TODO: optimize list API
    queryset = Contract.objects.all().select_related(
        "created_by",
        "member__stored_member",
        "campaign",
    )
    serializer_class = serializers.ContractDetailSerializer
    serializers_map = {
        "attach_level": serializers.LevelContractAttachSerializer,
        "create": serializers.ContractCreateUpdateSerializer,
        "update": serializers.ContractCreateUpdateSerializer,
        "get_interval_view": ContractPublicDetailSerializer,
        "default": serializers.ContractDetailSerializer,
    }
    permissions_map = {
        "attach_level": (
            IsAuthenticated,
            IsVolunteer,
            IsCampaignLive,
            ~IsChamberChair,
            IsDraftContract,
        ),
        "create": (
            IsAuthenticated,
            IsVolunteer,
            IsCampaignLive,
            ~IsChamberChair,
        ),
        "update": (
            IsAuthenticated,
            IsVolunteer,
            IsCampaignLive | IsCampaignRenewal,
            ~IsChamberChair,
            IsDraftContract,
        ),
        "destroy": (
            IsAuthenticated,
            IsVolunteer,
            ~IsChamberChair,
            IsDraftContract,
        ),
        "default": (AllowAllRoles,),
    }
    ordering_fields = ("name",)
    search_fields = (
        "name",
    )
    filterset_class = ContractFilter

    def get_queryset(self):
        """Return list of contracts created by current user."""
        campaign = getattr(self.request, "campaign", None)
        qs = super().get_queryset()
        if not campaign:
            return qs.none()
        return qs.annotate(
            private_note=models.F("note"),
        ).filter(
            campaign=campaign,
            created_by__user_id=self.request.user.id,
        ).with_level_count().with_total_cost().prefetch_related(
            models.Prefetch(
                "levels",
                queryset=LevelInstance.objects.all().select_related(
                    "level__product",
                ),
            ),
            models.Prefetch(
                "shared_credits_with",
                queryset=UserCampaign.objects.all(),
            ),
        ).select_related("campaign__chamber").order_by("name")

    def perform_destroy(self, instance):
        """Delete contract."""
        services.delete_contract(instance)

    @action(methods=("get",), detail=True, url_path="internal-view")
    def get_interval_view(self, *args, **kwargs):
        """Return contract information for interval view."""
        contract = self.get_object()
        serializer = self.get_serializer(contract)
        return response.Response(serializer.data)

    @action(methods=("post",), detail=True, url_path="attach-level")
    def attach_level(self, request, *args, **kwargs) -> response.Response:
        """Attach level to an existing contract."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        level = serializer.validated_data.get("level")
        contract = self.get_object()
        level_instance = LevelInstance.from_level(level=level)
        level_instance.contract = contract
        level_instance.save()
        return response.Response(data=_("Attach product successfully."))
