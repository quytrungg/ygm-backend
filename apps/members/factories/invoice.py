import factory

from ..models import Invoice


class InvoiceFactory(factory.django.DjangoModelFactory):
    """Create instance of Invoice model."""

    is_paid = factory.Faker("pybool")
    name = factory.Faker("word")
    sent_at = factory.Faker("date_time")
    contract = factory.SubFactory("apps.members.factories.ContractFactory")

    class Meta:
        model = Invoice
