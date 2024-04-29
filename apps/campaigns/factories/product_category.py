import factory

from ..models import ProductCategory


class ProductCategoryFactory(factory.django.DjangoModelFactory):
    """Create instance of ProductCategory model."""

    name = factory.Faker("word")
    image = factory.Faker("url")
    campaign = factory.SubFactory("apps.campaigns.factories.CampaignFactory")

    class Meta:
        model = ProductCategory
