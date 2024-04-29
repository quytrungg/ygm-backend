import factory

from ..models import Level


class LevelFactory(factory.django.DjangoModelFactory):
    """Create instance of Level model."""

    name = factory.Faker("word")
    amount = factory.Faker("pyint", min_value=10)
    benefits = factory.Faker("sentence")
    description = factory.Faker("sentence")
    conditions = factory.Faker("sentence")
    product = factory.SubFactory("apps.campaigns.factories.ProductFactory")
    cost = factory.Faker(
        "pydecimal",
        left_digits=10,
        right_digits=2,
        positive=True,
    )

    class Meta:
        model = Level
