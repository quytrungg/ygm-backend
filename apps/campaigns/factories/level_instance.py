import factory

from ..models import LevelInstance


class LevelInstanceFactory(factory.django.DjangoModelFactory):
    """Create instance of LevelInstance model."""

    declined_at = None
    level = factory.SubFactory("apps.campaigns.factories.LevelFactory")
    contract = factory.SubFactory("apps.members.factories.ContractFactory")
    cost = factory.Faker(
        "pydecimal",
        left_digits=10,
        right_digits=2,
        positive=True,
    )

    class Meta:
        model = LevelInstance
