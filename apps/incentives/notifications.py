from django.conf import settings

from libs.notifications.email import NoteEmailNotification

from apps.campaigns.constants import NoteType
from apps.campaigns.context_managers import RewardContextManager
from apps.campaigns.models import Note
from apps.incentives.models import Reward


class RewardEmailNotification(NoteEmailNotification):
    """Send invitation email to campaign's volunteer."""

    def __init__(self, reward: Reward, **template_context):
        super().__init__(**template_context)
        note = Note.objects.get(
            campaign=reward.incentive.campaign,
            type=NoteType.REWARD_EMAIL,
        )
        self.reward = reward
        self.context_manager = RewardContextManager(
            note=note,
            reward=reward,
        )

    def get_formatted_subject(self):
        campaign = self.reward.incentive.campaign
        return f"{campaign.chamber.name} - {campaign.name} Reward Update"

    def get_recipient_list(self) -> list[str]:
        """Return volunteer email."""
        return [self.reward.user_campaign.email]

    def send(self) -> bool:
        """Temporarily disable on production env."""
        if settings.ENVIRONMENT in ("production", "prod"):
            return False
        return super().send()
