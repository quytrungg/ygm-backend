import uuid

import factory

from ..models import Chamber


class ChamberFactory(factory.django.DjangoModelFactory):
    """Factory to generate test Chamber instances."""

    name = factory.Faker("company")
    nickname = factory.Faker("uuid4")
    address = factory.Faker("address")
    city = factory.Faker("city")
    country = factory.Faker("country")
    zipcode = factory.Faker("postcode")
    state = factory.Faker("pystr", min_chars=2, max_chars=2)
    phone = factory.Faker(
        "pystr_format",
        string_format="######{{random_int}}",
    )
    mail_address = factory.Faker("address")
    member_count = factory.Faker("pyint", min_value=0, max_value=100)
    city_population = factory.Faker("pyint", min_value=0)
    country_population = factory.Faker("pyint", min_value=0)
    msa_population = factory.Faker("pyint", min_value=0)
    total_budget = factory.Faker(
        "pydecimal",
        positive=True,
        right_digits=2,
        left_digits=5,
    )
    total_membership_budget = factory.Faker(
        "pydecimal",
        positive=True,
        right_digits=2,
        left_digits=5,
    )
    pre_income = factory.Faker(
        "pydecimal",
        positive=True,
        right_digits=2,
        left_digits=5,
    )
    trc_coord_first_name = factory.Faker("first_name")
    trc_coord_last_name = factory.Faker("last_name")
    trc_coord_email = factory.Faker("email")
    trc_coord_phone = factory.Faker(
        "pystr_format",
        string_format="######{{random_int}}",
    )
    trc_coord_title = factory.Faker("job")
    trc_coord_office_phone = factory.Faker(
        "pystr_format",
        string_format="######{{random_int}}",
    )
    trc_coord_office_phone_ext = factory.Faker(
        "pystr_format",
        string_format="{{random_int}}",
    )
    ceo_first_name = factory.Faker("first_name")
    ceo_last_name = factory.Faker("last_name")
    ceo_email = factory.Faker("email")
    ceo_phone = factory.Faker(
        "pystr_format",
        string_format="######{{random_int}}",
    )
    instagram_url = factory.Faker("url")
    facebook_url = factory.Faker("url")
    twitter_url = factory.Faker("url")
    youtube_url = factory.Faker("url")
    linkedin_url = factory.Faker("url")

    @factory.lazy_attribute
    def subdomain(self):
        """Return a unique subdomain."""
        return f"{uuid.uuid4()}"

    class Meta:
        model = Chamber
