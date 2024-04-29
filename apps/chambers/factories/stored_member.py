import factory

from ..models import StoredMember


class StoredMemberFactory(factory.django.DjangoModelFactory):
    """Create instance of StoredMember model."""

    chamber = factory.SubFactory("apps.chambers.factories.ChamberFactory")
    name = factory.Faker("name")
    address = factory.Faker("word")
    city = factory.Faker("word")
    state = "CA"
    zip = factory.Faker("random_number", digits=5)
    phone = factory.Faker("random_number", digits=10)

    class Meta:
        model = StoredMember
