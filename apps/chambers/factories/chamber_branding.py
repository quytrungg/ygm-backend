import factory

from ..models import ChamberBranding


class ChamberBrandingFactory(factory.django.DjangoModelFactory):
    """Factory to generate test ChamberBranding instances."""

    chamber = factory.SubFactory(
        "apps.chambers.factories.ChamberFactory",
    )
    site_primary_color = factory.Faker("color")
    site_secondary_color = factory.Faker("color")
    site_alternate_color = factory.Faker("color")
    headline = factory.Faker("sentence", nb_words=2)
    public_prelaunch_msg = factory.Faker("sentence")
    volunteer_prelaunch_msg = factory.Faker("sentence")

    class Meta:
        model = ChamberBranding
