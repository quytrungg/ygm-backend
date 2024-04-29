import factory

from apps.incentives.models import Reward


class RewardFactory(factory.django.DjangoModelFactory):
    """Create instances of Reward model."""

    incentive = factory.SubFactory(
        "apps.incentives.factories.IncentiveFactory",
    )
    user_campaign = factory.SubFactory(
        "apps.campaigns.factories.UserCampaignFactory",
    )
    paid_at = factory.Faker("date_time_this_year")

    class Meta:
        model = Reward
