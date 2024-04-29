import factory
from factory.fuzzy import FuzzyChoice

from ..constants import TimelineStatus
from ..models import Timeline, TimelineType


class TimelineFactory(factory.django.DjangoModelFactory):
    """Factory to generate test Task instances."""

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    due_date = factory.Faker("date_time")
    type = factory.Faker(
        "random_element",
        elements=TimelineType.objects.all(),
    )
    status = FuzzyChoice(
        TimelineStatus.choices,
        getter=lambda stat: stat[0],
    )
    category = factory.SubFactory(
        "apps.timelines.factories.TimelineCategoryFactory",
    )
    created_by = factory.SubFactory(
        "apps.users.factories.UserFactory",
    )
    assigned_to = factory.Faker("word")
    chamber = factory.SubFactory(
        "apps.chambers.factories.ChamberFactory",
    )

    class Meta:
        model = Timeline
