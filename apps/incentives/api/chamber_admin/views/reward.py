from decimal import Decimal

from django.db import models
from django.db.models import Prefetch
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.functional import partition

from rest_framework import mixins, response
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView

from apps.campaigns.models import UserCampaign
from apps.core.api.permissions import AllowChamberAdmin, IsCampaignInProgress
from apps.core.api.views import ChamberAPIViewMixin, ChamberBaseViewSet
from apps.incentives.models import Reward
from apps.incentives.services import incentive_services, reward_services

from .. import serializers


class RallySessionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    ChamberBaseViewSet,
):
    """Viewset for chamber admin to manage rally session."""

    queryset = UserCampaign.objects.all().with_member_name()
    serializer_class = serializers.RallySessionUserCampaignSerializer
    serializers_map = {
        "get_session_weeks": serializers.RallySessionWeekSerializer,
    }
    permissions_map = {
        "default": (AllowChamberAdmin,),
    }
    search_fields = (
        "first_name",
        "last_name",
        "member_name",
    )
    ordering_fields = ()

    def get_queryset(self):
        """Return users with revenue and reward info."""
        qs = super().get_queryset()
        session_start, session_end = self.get_selected_session_range()
        if getattr(self, "swagger_fake_view", False):
            return qs.none()

        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()

        qs = (
            qs.with_week_revenue(
                revenue_from=session_start,
                revenue_to=session_end,
            )
            .with_week_paid_reward_amount(
                paid_from=session_start,
                paid_to=session_end,
            )
            .filter(campaign_id=campaign.id, week_revenue__gt=0)
            .prefetch_related(
                models.Prefetch(
                    "rewards",
                    queryset=Reward.objects.all().select_related("incentive"),
                ),
            )
            .order_by("-week_revenue", "id")
        )
        return qs

    def get_selected_session_range(self):
        """Return the selected session range for filtering reward."""
        if getattr(self, "swagger_fake_view", False):
            return None, None
        rally_session_week_serializer = serializers.RallySessionWeekSerializer(
            data=self.request.query_params,
        )
        rally_session_week_serializer.is_valid(raise_exception=True)
        validated_data = rally_session_week_serializer.validated_data
        return validated_data["session_start"], validated_data["session_end"]

    @action(methods=("GET",), url_path="weeks", detail=False)
    def get_session_weeks(self, request, *args, **kwargs):
        """Return weeks of rally session."""
        campaign = getattr(request, "campaign", None)
        response_data = []

        if campaign:
            weeks = reward_services.get_rally_session_weeks(
                campaign=campaign,
                current_date=timezone.localdate(timezone=campaign.timezone),
            )
            with timezone.override(campaign.timezone):
                serializer = self.get_serializer(
                    [
                        {"session_start": week[0], "session_end": week[1]}
                        for week in weeks
                    ],
                    many=True,
                )
                response_data = serializer.data
        return response.Response(data={"results": response_data})


class PaidAndOwedRewardViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    ChamberBaseViewSet,
):
    """Return volunteers with paid and owed reward values."""

    serializer_class = serializers.PaidAndOwedRewardSerializer
    queryset = UserCampaign.objects.all().can_sell_contract()
    permissions_map = {
        "default": (AllowChamberAdmin,),
    }
    search_fields = ()
    ordering_fields = ()

    def get_queryset(self):
        """Return users with rewards, paid and owed info."""
        qs = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return qs.none()

        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()

        return qs.filter(campaign_id=campaign.id).prefetch_related(
            models.Prefetch(
                "rewards",
                queryset=Reward.objects.all().select_related("incentive"),
            ),
        ).annotate(
            total_owed=Coalesce(
                models.Sum(
                    "rewards__incentive__value",
                    filter=models.Q(rewards__paid_at__isnull=True),
                ),
                Decimal(0),
            ),
            total_paid=Coalesce(
                models.Sum(
                    "rewards__incentive__value",
                    filter=models.Q(rewards__paid_at__isnull=False),
                ),
                Decimal(0),
            ),
        ).order_by("total_paid")


class RewardViewSet(
    ChamberBaseViewSet,
):
    """Provide viewset for CA to manage rewards."""

    serializer_class = serializers.RewardMetricsSerializer
    queryset = Reward.objects.all().select_related("incentive")
    serializers_map = {
        "get_stats": serializers.RewardMetricsSerializer,
        "accumulating_levels": serializers.RewardAccumulatingLevelSerializer,
    }
    permissions_map = {
        "default": (AllowChamberAdmin,),
    }
    search_fields = ()
    ordering_fields = ()

    def get_queryset(self):
        """Return rewards queryset."""
        qs = super().get_queryset()
        if getattr(self, "swagger_fake_view", False):
            return qs.none()

        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()

        return qs.filter(incentive__campaign=campaign)

    @action(methods=("get",), detail=False, url_path="stats")
    def get_stats(self, request, *args, **kwargs) -> response.Response:
        """Provide incentive metrics within campaign."""
        rewards = self.get_queryset()
        reward_metrics = incentive_services.get_reward_metrics(rewards)
        serializer = self.get_serializer(reward_metrics)
        return response.Response(data=serializer.data)

    @action(methods=("get",), detail=True, url_path="accumulating-levels")
    def accumulating_levels(self, request, *args, **kwargs):
        """Return levels accumulating to a reward."""
        campaign = getattr(request, "campaign", None)
        if not campaign:
            return self.get_paginated_response([])

        reward: Reward = self.get_object()
        serializer = self.get_serializer(
            reward_services.get_sold_levels_accumulating_to_reward(reward),
            many=True,
        )
        with timezone.override(campaign.timezone):
            response_data = serializer.data
        page = self.paginate_queryset(response_data)
        return self.get_paginated_response(page)


class RewardMarkPaymentStatusAPIView(
    ChamberAPIViewMixin,
    GenericAPIView,
):
    """Provide API to update rewards payment statuses."""

    queryset = Reward.objects.all()
    serializer_class = serializers.RewardMarkPaymentStatusSerializer
    permission_classes = (AllowChamberAdmin, IsCampaignInProgress)

    def put(self, request, *args, **kwargs):
        """Update rewards' payment statuses."""
        serializer = self.get_serializer(
            data=request.data,
            many=True,
        )
        serializer.is_valid(raise_exception=True)
        ids_marked_unpaid, ids_marked_paid = self._group_reward_ids(
            validated_data=serializer.validated_data,
        )
        campaign = getattr(request, "campaign", None)
        campaign_id = getattr(campaign, "id", None)
        reward_services.mark_rewards_as_paid(
            campaign_id=campaign_id,
            reward_ids=ids_marked_paid,
        )
        reward_services.mark_rewards_as_unpaid(
            campaign_id=campaign_id,
            reward_ids=ids_marked_unpaid,
        )
        return response.Response()

    def _group_reward_ids(
        self,
        validated_data,
    ) -> tuple[list[int], list[int]]:
        """Return reward ids grouped by marked payment status."""
        items_marked_unpaid, items_marked_paid = partition(
            values=validated_data,
            predicate=lambda item: item["is_paid"],
        )
        return (
            [item["id"] for item in items_marked_unpaid],
            [item["id"] for item in items_marked_paid],
        )


class PayoutMetricsAPIView(ChamberAPIViewMixin, GenericAPIView):
    """Provide api view to provide payout metrics for volunteers."""

    serializer_class = serializers.PayoutMetricsSerializer
    queryset = UserCampaign.objects.all().can_sell_contract().prefetch_related(
        Prefetch(
            "rewards",
            queryset=Reward.objects.select_related("incentive"),
        ),
    )

    def get(self, request, *args, **kwargs) -> response.Response:
        """Return payout metrics for a specific volunteer."""
        volunteer = self.get_object()
        payout_metrics = incentive_services.get_payout_metrics(volunteer)
        serializer = self.get_serializer(payout_metrics)
        return response.Response(data=serializer.data)
