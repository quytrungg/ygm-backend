import factory

from ..models import Product


class ProductFactory(factory.django.DjangoModelFactory):
    """Create instance of Product model."""

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    is_included_in_renewal = True
    category = factory.SubFactory(
        "apps.campaigns.factories.ProductCategoryFactory",
    )
    pre_trc_income = factory.Faker(
        "pydecimal",
        left_digits=10,
        right_digits=2,
        positive=True,
    )

    class Meta:
        model = Product
