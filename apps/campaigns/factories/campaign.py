from datetime import date

import factory
from factory.fuzzy import FuzzyChoice

from apps.core.constants import AvailableTimezone

from ..constants import CampaignStatus
from ..models import Campaign


class CampaignFactory(factory.django.DjangoModelFactory):
    """Create instance of Campaign model."""

    name = factory.Faker("word")
    year = factory.Faker("pyint", min_value=2000, max_value=3000)
    chamber = factory.SubFactory("apps.chambers.factories.ChamberFactory")
    status = FuzzyChoice(CampaignStatus.values)
    goal = factory.Faker(
        "pydecimal",
        left_digits=10,
        right_digits=2,
        positive=True,
    )
    start_date = date.today()
    end_date = date(date.today().year, 12, 31)
    timezone = FuzzyChoice(AvailableTimezone.values)

    class Meta:
        model = Campaign
