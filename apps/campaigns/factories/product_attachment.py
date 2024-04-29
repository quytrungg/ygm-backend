import factory

from ..models import ProductAttachment


class ProductAttachmentFactory(factory.django.DjangoModelFactory):
    """Create instance of ProductAttachment model."""

    name = factory.Faker("word")
    file = factory.Faker("url")
    content_type = factory.Faker("word")
    product = factory.SubFactory("apps.campaigns.factories.ProductFactory")

    class Meta:
        model = ProductAttachment
