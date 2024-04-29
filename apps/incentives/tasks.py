from collections.abc import Collection

from config.celery import app

from apps.incentives.models import Reward
from apps.incentives.notifications import RewardEmailNotification


@app.task
def send_reward_emails(reward_ids: Collection[int]):
    """Send reward email."""
    rewards = Reward.objects.filter(id__in=reward_ids)
    for reward in rewards:
        email = RewardEmailNotification(reward=reward)
        email.send()
