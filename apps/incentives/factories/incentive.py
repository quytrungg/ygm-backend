import factory
from factory.fuzzy import FuzzyChoice

from apps.campaigns.factories import CampaignFactory

from ..constants import IncentiveType
from ..models import Incentive


class IncentiveFactory(factory.django.DjangoModelFactory):
    """Create instance of Incentive model."""

    name = factory.Faker("word")
    threshold = factory.Faker(
        "pydecimal",
        positive=True,
        right_digits=2,
        left_digits=5,
    )
    value = factory.Faker(
        "pydecimal",
        positive=True,
        right_digits=2,
        left_digits=5,
    )
    type = FuzzyChoice(
        IncentiveType.choices,
        getter=lambda type: type[0],
    )
    campaign = factory.SubFactory(CampaignFactory)

    class Meta:
        model = Incentive
