from django.db.models import QuerySet

from apps.campaigns.models import UserCampaign

from ..constants import IncentiveType
from ..models import Reward


def get_reward_metrics(rewards: QuerySet[Reward]) -> dict:
    """Return incentive metrics within campaign."""
    paid_incentives = sum(
        reward.incentive.value for reward in rewards if reward.paid_at
    )
    owed_incentives = sum(
        reward.incentive.value for reward in rewards if not reward.paid_at
    )
    return {
        "total_incentives": paid_incentives + owed_incentives,
        "paid_incentives": paid_incentives,
        "owed_incentives": owed_incentives,
    }


def get_payout_metrics(volunteer: UserCampaign) -> dict:
    """Return payout metrics for volunteer."""
    rewards = volunteer.rewards.all()
    total_cash = sum(
        reward.incentive.value
        for reward in rewards if reward.incentive.type == IncentiveType.CASH
    )
    total_trade = sum(
        reward.incentive.value
        for reward in rewards if reward.incentive.type == IncentiveType.TRADE
    )
    total_paid = sum(
        reward.incentive.value for reward in rewards if reward.paid_at
    )
    return {
        "total_cash": total_cash,
        "total_trade": total_trade,
        "total_overall": total_cash + total_trade,
        "total_paid": total_paid,
    }
