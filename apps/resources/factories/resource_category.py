import factory

from ..models import ResourceCategory


class ResourceCategoryFactory(factory.django.DjangoModelFactory):
    """Create instance of ResourceCategory."""

    name = factory.Faker("word")

    class Meta:
        model = ResourceCategory
