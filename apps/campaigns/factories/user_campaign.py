import factory
from factory.fuzzy import FuzzyChoice

from apps.campaigns.constants import UserCampaignRole

from ..models import UserCampaign


class UserCampaignFactory(factory.django.DjangoModelFactory):
    """Create test instance of Team model."""

    first_name = factory.Faker("word")
    last_name = factory.Faker("word")
    email = factory.Faker("email")
    company_name = factory.Faker("word")
    role = FuzzyChoice(
        UserCampaignRole.choices,
        getter=lambda status: status[0],
    )
    team = factory.SubFactory("apps.campaigns.factories.TeamFactory")
    campaign = factory.SubFactory("apps.campaigns.factories.CampaignFactory")
    user = factory.SubFactory("apps.users.factories.VolunteerFactory")

    class Meta:
        model = UserCampaign
