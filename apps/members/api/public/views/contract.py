from django.db import models

from rest_framework import mixins, response, status
from rest_framework.decorators import action

from apps.campaigns.models import LevelInstance
from apps.core.api import views
from apps.members.models import Contract

from ...common.serializers import ContractPublicDetailSerializer
from ...permissions import IsContractCampaignLiveOrRenewal, IsSignableContract
from ..serializers import ContractSignSerializer


class ContractViewSet(
    mixins.RetrieveModelMixin,
    views.BaseViewSet,
):
    """Viewset to manage public contracts for members/unregistered users."""

    queryset = Contract.objects.all().select_related(
        "member",
        "campaign",
        "campaign__chamber",
    ).annotate(private_note=models.Value(""))
    authentication_classes = ()
    lookup_field = "token"
    serializer_class = ContractPublicDetailSerializer
    serializers_map = {
        "sign": ContractSignSerializer,
        "default": ContractPublicDetailSerializer,
    }
    permissions_map = {
        "sign": (IsContractCampaignLiveOrRenewal, IsSignableContract),
        "default": (IsContractCampaignLiveOrRenewal,),
    }

    def get_queryset(self):
        """Annotate additional information."""
        qs = super().get_queryset()
        return qs.with_level_count().with_total_cost().prefetch_related(
            models.Prefetch(
                "levels",
                queryset=LevelInstance.objects.all().select_related(
                    "level__product",
                ),
            ),
        ).order_by("name")

    @action(methods=("post",), detail=True)
    def sign(self, request, *args, **kwargs) -> response.Response:
        """Sign a contract for member/unregistered user."""
        contract = self.get_object()
        serializer = self.get_serializer(contract, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )
