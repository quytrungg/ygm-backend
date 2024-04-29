import factory

from ..models import TimelineAttachment


class TimelineAttachmentFactory(factory.django.DjangoModelFactory):
    """Create instance of TimelineAttachment model."""

    name = factory.Faker("word")
    file = factory.Faker("url")
    content_type = factory.Faker("word")
    timeline = factory.SubFactory("apps.timelines.factories.TimelineFactory")

    class Meta:
        model = TimelineAttachment
