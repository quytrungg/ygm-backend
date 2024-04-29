from django.db import models
from django.db.models.functions import Concat

from rest_framework import mixins, response
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema

from libs.api.filter_backends import CustomDjangoFilterBackend
from libs.open_api.filters import SearchFilterBackend

from apps.campaigns.models import LevelInstance
from apps.core.api import views
from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.permissions import (
    AllowChamberAdmin,
    IsCampaignLive,
    IsCampaignRenewal,
)
from apps.members.models import Contract

from .... import services
from ....constants import ContractStatus
from ...common.serializers import (
    ContractListSerializer,
    ContractPublicDetailSerializer,
)
from ...filters import ContractFilter, ContractOrderingFilterBackend
from ...permissions import IsDraftContract
from ..serializers import (
    ContractApproveSerializer,
    ContractEditCreditsSerializer,
    ContractReassignSerializer,
    ContractUpdateSerializer,
)


class ContractViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    UpdateModelWithoutPatchMixin,
    mixins.DestroyModelMixin,
    views.ChamberBaseViewSet,
):
    """Contract management for chamber admin and super admin."""

    queryset = Contract.objects.all()
    serializer_class = ContractListSerializer
    filterset_class = ContractFilter
    filter_backends = (
        CustomDjangoFilterBackend,
        ContractOrderingFilterBackend,
        SearchFilterBackend,
    )
    ordering_fields = (
        "name",
        "status",
        "levels_count",
        "total_cost",
        "member_name",
        "created_by_name",
        "signed_at",
        "approval_priority",
    )
    serializers_map = {
        "list": ContractListSerializer,
        "retrieve": ContractPublicDetailSerializer,
        "approve": ContractApproveSerializer,
        "reassign": ContractReassignSerializer,
        "share_credits": ContractEditCreditsSerializer,
        "update": ContractUpdateSerializer,
        "default": ContractListSerializer,
    }
    permissions_map = {
        "destroy": (AllowChamberAdmin, IsDraftContract),
        "approve": (AllowChamberAdmin, IsCampaignLive | IsCampaignRenewal),
        "decline": (AllowChamberAdmin, IsCampaignLive | IsCampaignRenewal),
        "default": (AllowChamberAdmin,),
    }
    search_fields = (
        "name",
    )

    def get_queryset(self):
        """Return contracts of current user's chamber."""
        qs = super().get_queryset().alias(
            created_by_name=Concat(
                models.F("created_by__first_name"),
                models.Value(" "),
                models.F("created_by__last_name"),
            ),
            member_name=models.F("member__name"),
        ).annotate(
            status_priority_for_approval=models.Case(
                *[
                    models.When(status=status, then=order)
                    for order, status in enumerate(
                        ContractStatus.get_order_by_approval_priority(),
                    )
                ],
            ),
        ).with_level_count().with_total_cost()
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()

        qs = qs.select_related(
            "member",
            "campaign",
            "created_by__user",
        ).annotate(
            private_note=models.Case(
                models.When(
                    created_by__user_id=user.id,
                    then=models.F("note"),
                ),
                default=models.Value(""),
                output_field=models.CharField(),
            ),
        )
        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()
        if self.action == "retrieve":
            qs = qs.prefetch_related(
                models.Prefetch(
                    "levels",
                    queryset=LevelInstance.objects.all().select_related(
                        "level__product",
                    ),
                ),
            )
        return qs.filter(campaign_id=campaign.id)

    def perform_destroy(self, instance):
        """Delete contract."""
        services.delete_contract(instance)

    @action(methods=("post",), detail=True)
    def approve(self, request, *args, **kwargs) -> response.Response:
        """Approve the contract."""
        contract = self.get_object()
        serializer = self.get_serializer(contract, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response()

    @action(methods=("post",), detail=True)
    def decline(self, *args, **kwargs) -> response.Response:
        """Decline the contract."""
        contract = self.get_object()
        services.decline_contract(contract)
        return response.Response()

    @extend_schema(request=ContractReassignSerializer(many=True))
    @action(methods=("post",), detail=False)
    def reassign(self, request, *args, **kwargs) -> response.Response:
        """Reassign multiple contracts to new users."""
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        services.reassign_contracts(reassign_data=serializer.validated_data)
        return response.Response(data=serializer.data)

    @action(methods=("put",), detail=True, url_path="share-credits")
    def share_credits(self, request, *args, **kwargs) -> response.Response:
        """Share a contract to some volunteers."""
        contract = self.get_object()
        serializer = self.get_serializer(contract, data=request.data)
        serializer.is_valid(raise_exception=True)
        services.set_contract_credits(
            contract=contract,
            shared_volunteers=serializer.validated_data["shared_credits_with"],
        )
        return response.Response(data=serializer.data)
