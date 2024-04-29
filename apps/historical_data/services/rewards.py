from typing import Iterable

from django.db.backends.mysql.base import CursorWrapper
from django.db.models import OuterRef, Subquery
from django.utils import timezone

from apps.campaigns.models import UserCampaign
from apps.chambers.models import Chamber
from apps.historical_data.services import RewardData
from apps.incentives.models import Incentive, Reward
from apps.users.models import User

REWARD_FETCH_SQL_TEMPLATE = """
SELECT
    id,
    user,
    chamber,
    reward
FROM paid_rewards
WHERE user is not NULL and chamber in ({list_of_ids})
"""


def fetch_reward_data(
    cursor: CursorWrapper,
    old_campaign_ids: Iterable[int],
) -> list[RewardData]:
    """Select rewards from old db."""
    query = REWARD_FETCH_SQL_TEMPLATE.format(
        list_of_ids=", ".join(["%s" for _ in old_campaign_ids]),
    )
    cursor.execute(query, tuple(old_campaign_ids))
    raw_rewards = cursor.fetchall()
    rewards: list[RewardData] = [
        RewardData(
            id=reward[0],
            user=reward[1],
            chamber=reward[2],
            reward=reward[3],
        ) for reward in raw_rewards
    ]
    return rewards


def import_chamber_rewards(
    cursor: CursorWrapper,
    old_campaign_ids: Iterable[int],
    target_chamber: Chamber,
) -> Iterable[int]:
    """Import old chamber rewards."""
    old_rewards: list[RewardData] = fetch_reward_data(
        cursor=cursor,
        old_campaign_ids=old_campaign_ids,
    )
    new_rewards = []
    incentive_ids_map: dict[int, int] = dict(
        Incentive.objects.filter(
            campaign__chamber_id=target_chamber.id,
            external_id__isnull=False,
        ).values_list("external_id", "id"),
    )
    user_ids_map: dict[int, int] = dict(
        User.objects.filter(
            external_id__isnull=False,
            chamber_id=target_chamber.id,
        ).annotate(
            latest_user_campaign_id=Subquery(
                UserCampaign.objects.filter(
                    user=OuterRef("pk"),
                ).order_by("-id").values("id")[:1],
            ),
        ).values_list("external_id", "latest_user_campaign_id"),
    )
    now = timezone.now()
    for reward in old_rewards:
        user_campaign_id = user_ids_map.get(reward.user)
        incentive_id = incentive_ids_map.get(reward.reward)
        new_rewards.append(
            Reward(
                incentive_id=incentive_id,
                user_campaign_id=user_campaign_id,
                paid_at=now,
                external_id=reward.id,
            ),
        )
    Reward.objects.bulk_create(new_rewards)
    return [reward.id for reward in new_rewards]
