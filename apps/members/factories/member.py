import factory

from ..models import Member


class MemberFactory(factory.django.DjangoModelFactory):
    """Create instance of Member model."""

    name = factory.Faker("name")
    title = factory.Faker("word")
    email = factory.Faker("email")
    address = factory.Faker("word")
    city = factory.Faker("word")
    state = "CA"
    zipcode = factory.Faker("random_number", digits=5)
    country = factory.Faker("word")
    phone = factory.Faker("random_number", digits=10)
    fax = factory.Faker("random_number", digits=10)
    contact_methods = factory.Faker("word")

    class Meta:
        model = Member
