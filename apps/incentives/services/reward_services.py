import datetime as dt
from collections import abc

from django.db.models import F, QuerySet
from django.utils import timezone

from dateutil import rrule

from apps.campaigns import models as campaigns_models
from apps.incentives.tasks import send_reward_emails

from .. import models


def create_new_rewards_for_volunteers(
    campaign_id: int,
    volunteer_ids: abc.Collection[int],
) -> list[models.Reward]:
    """Create rewards for some specific volunteers."""
    new_rewards = _get_new_rewards_for_volunteers(campaign_id, volunteer_ids)
    rewards = models.Reward.objects.bulk_create(new_rewards)
    if rewards:
        new_reward_ids = [reward.id for reward in rewards]
        send_reward_emails.delay(new_reward_ids)
    return rewards


def _get_new_rewards_for_volunteers(
    campaign_id: int,
    volunteer_ids: abc.Collection[int],
) -> list[models.Reward]:
    """Return new rewards for specific volunteers."""
    volunteers = (
        campaigns_models.UserCampaign.objects.all().can_sell_contract()
        .filter(
            id__in=volunteer_ids,
            campaign_id=campaign_id,
        )
        .prefetch_related(
            "rewards",
        )
        .with_total_revenue()
        .with_total_cash_revenue()
        .with_total_trade_revenue()
    )

    campaign_incentives = models.Incentive.objects.filter(
        campaign_id=campaign_id,
    )
    new_rewards = []
    for volunteer in volunteers:
        new_rewards.extend(
            _get_new_rewards_for_one_volunteer(
                volunteer=volunteer,
                incentives=campaign_incentives,
            ),
        )
    return new_rewards


def _get_new_rewards_for_one_volunteer(
    volunteer: campaigns_models.UserCampaign,
    incentives: QuerySet[models.Incentive],
) -> list[models.Reward]:
    """Return new rewards for a volunteer."""
    volunteer_rewarded_incentive_ids = volunteer.rewards.values_list(
        "incentive_id",
        flat=True,
    )
    not_rewarded_incentives = [
        incentive
        for incentive in incentives
        if incentive.id not in volunteer_rewarded_incentive_ids
    ]
    newly_qualified_incentives = [
        incentive
        for incentive in not_rewarded_incentives
        if incentive.is_achieved_by(volunteer)
    ]
    return [
        models.Reward(incentive=incentive, user_campaign=volunteer)
        for incentive in newly_qualified_incentives
    ]


def mark_rewards_as_paid(campaign_id: int, reward_ids: abc.Collection[int]):
    """Mark rewards specified by ids as paid."""
    models.Reward.objects.filter(
        incentive__campaign_id=campaign_id,
        id__in=reward_ids,
    ).filter(paid_at__isnull=True).update(paid_at=timezone.now())


def mark_rewards_as_unpaid(campaign_id, reward_ids: abc.Collection[int]):
    """Mark rewards specified by ids as not paid."""
    models.Reward.objects.filter(
        incentive__campaign_id=campaign_id,
        id__in=reward_ids,
    ).update(paid_at=None)


def get_rally_session_weeks(
    campaign: campaigns_models.Campaign,
    current_date: dt.date,
) -> list[tuple[dt.datetime, dt.datetime]]:
    """Return weeks of campaign's rally session."""
    if not campaign.start_date:
        return []

    until_date = _find_next_date_with_weekday(
        weekday=campaign.report_close_weekday,
        date=campaign.end_date or current_date,
    )
    reports_start_from = dt.datetime.combine(
        campaign.start_date,
        campaign.report_close_time,
        tzinfo=campaign.timezone,
    )
    reports_end_at = dt.datetime.combine(
        until_date,
        campaign.report_close_time,
        tzinfo=campaign.timezone,
    )
    timelines = list(
        rrule.rrule(
            dtstart=reports_start_from,
            until=reports_end_at,
            freq=rrule.WEEKLY,
        ),
    )
    return [
        (timelines[idx], timelines[idx + 1] - dt.timedelta(microseconds=1))
        for idx in range(len(timelines) - 1)
    ]


def _find_next_date_with_weekday(weekday: int, date: dt.date) -> dt.date:
    """Return the closet date with specified `weekday`, start from `date`."""
    date_weekday = date.weekday()
    if date_weekday == weekday:
        return date
    if date_weekday < weekday:
        return date + dt.timedelta(days=weekday - date_weekday)
    return date + dt.timedelta(days=7 - (date_weekday - weekday))


def get_sold_levels_accumulating_to_reward(
    reward: models.Reward,
) -> QuerySet[campaigns_models.LevelInstance]:
    """Return sold levels which accumulates to a reward."""
    return campaigns_models.LevelInstance.objects.filter(
        contract__credits_info__user_campaign_id=reward.user_campaign_id,
        contract__approved_at__lte=reward.created,
    ).select_related(
        "contract",
        "level__product",
    ).annotate(
        credited_portion=F("contract__credits_info__portion"),
    )
