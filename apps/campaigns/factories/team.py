import factory

from ..models import Team


class TeamFactory(factory.django.DjangoModelFactory):
    """Create test instance of Team model."""

    name = factory.Faker("word")
    goal = factory.Faker(
        "pydecimal",
        left_digits=10,
        right_digits=2,
        positive=True,
    )
    campaign = factory.SubFactory("apps.campaigns.factories.CampaignFactory")

    class Meta:
        model = Team
