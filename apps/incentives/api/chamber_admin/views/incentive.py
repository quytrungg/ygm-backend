from rest_framework import mixins, response, status
from rest_framework.decorators import action

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.permissions import AllowChamberAdmin, IsCampaignInProgress
from apps.core.api.views import ChamberBaseViewSet
from apps.incentives.constants import (
    IncentiveQualifierAmount,
    IncentiveQualifierName,
)
from apps.incentives.models import Incentive

from .. import serializers


class IncentiveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    UpdateModelWithoutPatchMixin,
    mixins.DestroyModelMixin,
    ChamberBaseViewSet,
):
    """Viewset for chamber admin to manage Incentive.

    For `list` operation (`GET` method): the system will automatically
        filter the incentives of the currently open campaign of the
        chamber admin's chamber.

    For `create` operation (`POST` method): the system will automatically
        assign the newly created incentive to the currently open campaign
        of the chamber admin's chamber.

    """

    queryset = Incentive.objects.all().order_by("order")
    serializer_class = serializers.BaseIncentiveReadSerializer
    serializers_map = {
        "list": serializers.BaseIncentiveReadSerializer,
        "retrieve": serializers.IncentiveDetailCASerializer,
        "create": serializers.IncentiveWriteSerializer,
        "update": serializers.IncentiveWriteSerializer,
        "get_qualifier_amounts": serializers.QualifierAmountListSerializer,
        "get_qualifier_names": serializers.QualifierNameListSerializer,
        "reorder": serializers.IncentiveReorderSerializer,
        "default": serializers.BaseIncentiveReadSerializer,
    }
    permissions_map = {
        "default": (AllowChamberAdmin,),
        "reorder": (AllowChamberAdmin, IsCampaignInProgress),
    }
    search_fields = (
        "name",
    )
    ordering_fields = (
        "id",
        "name",
    )

    def get_queryset(self):
        """Return incentives of current user's campaign."""
        qs = super().get_queryset()

        if getattr(self, "swagger_fake_view", False):
            return qs.none()

        if self.action == "retrieve":
            qs = qs.prefetch_related("qualifiers")

        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()

        qs = qs.filter(campaign_id=campaign.id)
        return qs

    @action(detail=False, methods=("get",), url_path="qualifier-amounts")
    def get_qualifier_amounts(
        self,
        *args,
        **kwargs,
    ) -> response.Response:
        """Return all of incentive qualifier amount."""
        data = [
            {
                "value": amount.value,
                "label": amount.label,
            }
            for amount in IncentiveQualifierAmount
        ]

        serializer = self.get_serializer(data, many=True)

        return response.Response(
            status=status.HTTP_200_OK,
            data=serializer.data,
        )

    @action(detail=False, methods=("get",), url_path="qualifier-names")
    def get_qualifier_names(
        self,
        *args,
        **kwargs,
    ) -> response.Response:
        """Return all of incentive qualifier names."""
        data = [
            {
                "value": name.value,
                "label": name.label,
            }
            for name in IncentiveQualifierName
        ]

        serializer = self.get_serializer(data, many=True)

        return response.Response(
            status=status.HTTP_200_OK,
            data=serializer.data,
        )

    @action(methods=("put",), detail=True)
    def reorder(self, request, *args, **kwargs) -> response.Response:
        """Reorder item in incentive list data."""
        incentive = self.get_object()
        serializer = self.get_serializer(incentive, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response()
