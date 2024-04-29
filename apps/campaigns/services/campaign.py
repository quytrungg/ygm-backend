from decimal import Decimal

from django.db import models
from django.db.models.functions import Coalesce

from apps.campaigns import models as campaigns_models
from apps.incentives.constants import IncentiveType
from apps.incentives.models import Incentive
from apps.members.constants import ContractStatus
from apps.users.models import User

from ..models import Campaign, Level


def get_vs_dashboard_data(
    campaign: campaigns_models.Campaign,
    user: User,
) -> dict:
    """Return VS campaign dashboard data."""
    dashboard_data = {}
    dashboard_data.update(_get_vs_dashboard_campaign_data(campaign))
    if user.role == User.ROLES.SUPER_ADMIN:
        dashboard_data.update(_get_vs_dashboard_super_admin_fake_data())
    else:
        dashboard_data.update(_get_vs_dashboard_personal_data(campaign, user))

    return dashboard_data


def _get_vs_dashboard_campaign_data(campaign: campaigns_models.Campaign):
    """Return campaign's data in VS dashboard."""
    campaign_revenue = campaigns_models.LevelInstance.objects.filter(
        contract__campaign_id=campaign.id,
        contract__status=ContractStatus.APPROVED,
        declined_at__isnull=True,
    ).aggregate(
        revenue=Coalesce(models.Sum(models.F("cost")), Decimal(0)),
    )["revenue"]

    return {
        "campaign_goal": campaign.goal,
        "campaign_total": campaign_revenue,
    }


def _get_vs_dashboard_personal_data(
    campaign: campaigns_models.Campaign,
    user: User,
):
    """Return personal data in VS dashboard."""
    campaign_user = campaigns_models.UserCampaign.objects.filter(
        campaign_id=campaign.id,
        user_id=user.id,
    ).all().with_total_revenue().first()
    personal_revenue = campaign_user.total_revenue
    next_incentive = Incentive.objects.filter(
        campaign_id=campaign.id,
        threshold__gt=personal_revenue,
    ).order_by("threshold").first()
    trip_incentive = Incentive.objects.filter(
        campaign_id=campaign.id,
        type=IncentiveType.TRIP,
        threshold__gt=personal_revenue,
    ).order_by("threshold").first()
    next_threshold = (
        next_incentive.threshold if next_incentive else personal_revenue
    )
    trip_threshold = (
        trip_incentive.threshold if trip_incentive else personal_revenue
    )

    return {
        "total_raised": personal_revenue,
        "personal_goal": campaign_user.sales_goal if campaign_user else None,
        "next_incentive_threshold": next_threshold,
        "remaining_to_next_incentive": next_threshold - personal_revenue,
        "trip_incentive_threshold": trip_threshold,
        "remaining_to_trip_incentive": trip_threshold - personal_revenue,
    }


def _get_vs_dashboard_super_admin_fake_data():
    """Return fake data when SA access VS dashboard."""
    return {
        "total_raised": 0,
        "personal_goal": None,
        "next_incentive_threshold": 0,
        "remaining_to_next_incentive": 0,
        "trip_incentive_threshold": 0,
        "remaining_to_trip_incentive": 0,
    }


def complete_campaign(campaign: campaigns_models.Campaign):
    """Execute logic when campaign moves to `done` status."""
    campaigns_models.UserCampaign.objects.filter(
        campaign_id=campaign.id,
    ).update(is_active=False)


def get_inventory_stats(campaign: Campaign) -> dict:
    """Calculate statistics of campaign's inventory."""
    if not campaign:
        return {
            "total_value": Decimal(0),
            "levels_count": 0,
        }
    levels = Level.objects.filter(
        product__category__campaign_id=campaign.id,
    ).with_total_instances_count()
    total_value = sum(
        level.cost * level.total_instances_count
        for level in levels
        if level.amount > 0
    )
    return {
        "total_value": total_value,
        "levels_count": levels.count(),
    }


def get_chamber_newest_campaign(chamber) -> Campaign | None:
    """Return chamber's newest campaign."""
    try:
        return chamber.campaigns.latest("id")
    except Campaign.DoesNotExist:
        return None
