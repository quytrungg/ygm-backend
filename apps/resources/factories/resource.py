import factory

from ..models import Resource


class ResourceFactory(factory.django.DjangoModelFactory):
    """Create instance of Resource."""

    name = factory.Faker("word")
    file = factory.Faker("url")
    category = factory.SubFactory(
        "apps.resources.factories.ResourceCategoryFactory",
    )

    class Meta:
        model = Resource
