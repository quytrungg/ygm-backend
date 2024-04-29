import factory
from factory.fuzzy import FuzzyChoice

from ..constants import ContractStatus
from ..models import Contract


class ContractFactory(factory.django.DjangoModelFactory):
    """Create instance of Contract model."""

    name = factory.Faker("word")
    note = factory.Faker("word")
    created_by = factory.SubFactory(
        "apps.campaigns.factories.UserCampaignFactory",
    )
    member = factory.SubFactory("apps.members.factories.MemberFactory")
    campaign = factory.SubFactory("apps.campaigns.factories.CampaignFactory")
    status = FuzzyChoice(
        ContractStatus.choices,
        getter=lambda status: status[0],
    )

    class Meta:
        model = Contract
