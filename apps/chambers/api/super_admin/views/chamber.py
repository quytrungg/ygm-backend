from datetime import datetime

from django.core import exceptions
from django.db import models
from django.db.models.functions import Collate, Random
from django.utils.translation import gettext_lazy as _

from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.campaigns.services import get_chamber_newest_campaign
from apps.chambers.constants import ChamberRenewConfig
from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.views import AdminBaseViewSet
from apps.core.exceptions import NonFieldValidationError

from .... import services
from ....models import Chamber
from .. import serializers


class ChamberViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    UpdateModelWithoutPatchMixin,
    AdminBaseViewSet,
):
    """Viewset for super admin to manage Chamber."""

    queryset = Chamber.objects.all().prefetch_related("campaigns")
    serializer_class = serializers.ListChamberSerializer
    serializers_map = {
        "list": serializers.ListChamberSerializer,
        "retrieve": serializers.ChamberDetailSerializer,
        "create": serializers.ChamberCreateSerializer,
        "update": serializers.ChamberUpdateSerializer,
        "delete": serializers.ChamberDeleteVerifySerializer,
        "nickname_unique": serializers.ChamberNicknameCheckSerializer,
        "get_statistics": serializers.ChamberStatisticsSerializer,
        "get_renew_config": serializers.ChamberRenewConfigSerializer,
        "renew_campaign": serializers.ChamberCampaignRenewSASerializer,
        "default": serializers.ListChamberSerializer,
    }
    ordering_fields = ("sales", "nickname")
    search_fields = (
        "nickname_deterministic",
        "trc_coord_first_name",
        "trc_coord_last_name",
        "trc_coord_email",
    )

    def get_queryset(self):
        """Return chambers with additional sales info."""
        qs = super().get_queryset()
        return qs.annotate(
            sales=Random(
                output_field=models.DecimalField(
                    max_digits=15,
                    decimal_places=2,
                ),
            ),
            nickname_deterministic=Collate("nickname", "und-x-icu"),
        )

    @action(detail=True, methods=("post",))
    def delete(self, request, *args, **kwargs):
        """Soft delete Chamber only."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chamber = self.get_object()
        chamber.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=("get",), url_path="nickname-unique")
    def nickname_unique(self, request: Request, *args, **kwargs) -> Response:
        """Check if chamber nickname is unique."""
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        nickname = serializer.validated_data["nickname"]
        is_unique = not Chamber.objects.filter(nickname=nickname).exists()

        return Response({"unique": is_unique}, status=status.HTTP_200_OK)

    # TODO: replace with appropriate code after deciding
    @action(detail=True, methods=["get"], url_path="stats")
    def get_statistics(self, request, *args, **kwargs) -> Response:
        """Retrieve chamber statistics of the last four years."""
        year_serializer = self.get_serializer(data=request.query_params)
        year_serializer.is_valid(raise_exception=True)
        year = year_serializer.validated_data.get("year")
        data = self.get_statistics_data(year)
        page = self.paginate_queryset(data)
        return self.get_paginated_response(page)

    def get_statistics_data(self, year: int | None) -> list[dict[str, int]]:
        """Return the statistics data for the last four years."""
        data = [
            {
                "year": 2020,
                "trc_goal": 10000,
                "total_sale": 11000,
                "business_purchasing": 12000,
                "total_volunteers": 300,
            },
            {
                "year": 2021,
                "trc_goal": 20000,
                "total_sale": 21000,
                "business_purchasing": 22000,
                "total_volunteers": 400,
            },
            {
                "year": 2022,
                "trc_goal": 30000,
                "total_sale": 31000,
                "business_purchasing": 32000,
                "total_volunteers": 500,
            },
            {
                "year": 2023,
                "trc_goal": 40000,
                "total_sale": 41000,
                "business_purchasing": 42000,
                "total_volunteers": 600,
            },
        ]
        if not year:
            return data
        if year < datetime.now().year - 3 or year > datetime.now().year:
            return []
        return [data[year - 2020]]

    @action(methods=("get",), detail=True, url_path="renew-config")
    def get_renew_config(self, *args, **kwargs) -> Response:
        """Return chamber campaign renew config."""
        chamber = self.get_object()
        if not chamber.can_renew_campaign:
            error_msg = _(
                "Chamber is currently not available to renew campaign.",
            )
            return Response(
                data={"request": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )
        campaign = get_chamber_newest_campaign(chamber)
        config_data = [
            {"value": value, "label": label}
            for value, label in ChamberRenewConfig.choices
        ]
        response_data = {
            "config": config_data,
            "campaign_name": campaign.name,
        }
        serializer = self.get_serializer(response_data)
        return Response(data=serializer.data)

    @action(methods=("post",), detail=True, url_path="renew-campaign")
    def renew_campaign(self, request, *args, **kwargs) -> Response:
        """Renew chamber campaign with selected choices."""
        chamber = self.get_object()
        if not chamber.can_renew_campaign:
            error_msg = _(
                "Chamber is currently not available to renew campaign.",
            )
            return Response(
                data={"request": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            new_campaign_id = services.renew_chamber_campaign(
                chamber,
                serializer.validated_data,
            )
        except exceptions.ValidationError as exc:
            raise NonFieldValidationError(exc.messages) from exc
        response_data = {"renew_campaign_id": new_campaign_id}
        return Response(data=response_data)
