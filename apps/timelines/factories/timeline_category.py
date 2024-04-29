import factory

from ..models import TimelineCategory


class TimelineCategoryFactory(factory.django.DjangoModelFactory):
    """Create instance of TimelineCategory model."""

    name = factory.Faker("word")

    class Meta:
        model = TimelineCategory
