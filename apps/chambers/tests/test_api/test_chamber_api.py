# pylint: disable=too-many-lines
from datetime import datetime
from functools import partial

from django.urls import reverse, reverse_lazy

from rest_framework import status
from rest_framework.test import APIClient

import factory
import pytest
from knox.models import AuthToken

from apps.campaigns.constants import CampaignStatus
from apps.campaigns.factories import CampaignFactory
from apps.campaigns.models import (
    Campaign,
    Level,
    LevelInstance,
    Product,
    ProductCategory,
    Team,
    UserCampaign,
)
from apps.chambers import factories
from apps.chambers.models import Chamber, ChamberBranding
from apps.incentives.models import Incentive, IncentiveQualifier
from apps.members.models import Contract
from apps.users.constants import UserRole
from apps.users.factories import DEFAULT_PASSWORD, UserFactory
from apps.users.models import User


def get_chamber_url(action_name: str, kwargs=None):
    """Return url for super admin chamber api."""
    return reverse_lazy(f"v1:super-admin:chamber-{action_name}", kwargs=kwargs)


list_chamber_url = partial(get_chamber_url, action_name="list")()
detail_chamber_url = partial(get_chamber_url, action_name="detail")
chamber_nickname_unique_url = partial(
    get_chamber_url,
    action_name="nickname-unique",
)()
renew_chamber_campaign_url = partial(
    get_chamber_url,
    action_name="renew-campaign",
)


@pytest.fixture
def valid_chamber_nickname_data(chamber: Chamber) -> dict:
    """Return chamber data with unique nickname."""
    return {
        "name": "test chamber",
        "nickname": chamber.nickname * 2,
    }


@pytest.fixture
def invalid_chamber_nickname_data(chamber: Chamber) -> dict:
    """Return chamber data with duplicate nickname."""
    return {
        "name": "test chamber",
        "nickname": chamber.nickname,
    }


@pytest.fixture
def renew_chamber_campaign_config() -> dict:
    """Return config data to renew chamber campaign."""
    return {
        "name": "Renewed Campaign",
        "year": 2023,
        "inventory": True,
        "incentives": True,
        "users": True,
        "contracts": True,
    }


def test_chamber_nickname_unique_api_valid(
    super_admin_client: APIClient,
    valid_chamber_nickname_data: dict,
) -> None:
    """Ensure super admin can create new chamber with unique nickname."""
    response = super_admin_client.get(
        chamber_nickname_unique_url,
        data=valid_chamber_nickname_data,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["unique"]

    upper_nickname = valid_chamber_nickname_data["nickname"].upper()
    valid_chamber_nickname_data["nickname"] = upper_nickname
    response = super_admin_client.get(
        chamber_nickname_unique_url,
        data=valid_chamber_nickname_data,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["unique"]


def test_chamber_nickname_unique_api_invalid(
    super_admin_client: APIClient,
    invalid_chamber_nickname_data: dict,
) -> None:
    """Restrict super admin from create new chamber with duplicate nickname."""
    response = super_admin_client.get(
        chamber_nickname_unique_url,
        data=invalid_chamber_nickname_data,
    )
    assert response.status_code == status.HTTP_200_OK
    assert not response.data["unique"]

    # Ensure chamber nickname is case-insensitive for uniqueness checking
    upper_nickname = invalid_chamber_nickname_data["nickname"].upper()
    invalid_chamber_nickname_data["nickname"] = upper_nickname
    response = super_admin_client.get(
        chamber_nickname_unique_url,
        data=invalid_chamber_nickname_data,
    )
    assert response.status_code == status.HTTP_200_OK
    assert not response.data["unique"]


def test_chamber_nickname_unique_api_forbidden(
    valid_chamber_nickname_data: dict,
) -> None:
    """Ensure only super admin can create new chamber with valid data."""
    normal_user = UserFactory()
    normal_client = APIClient()
    normal_client.force_authenticate(normal_user)
    response = normal_client.get(
        chamber_nickname_unique_url,
        data=valid_chamber_nickname_data,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_chamber_statistics_api(
    api_client: APIClient,
    super_admin: User,
    chamber: Chamber,
) -> None:
    """Ensure chamber statistic API works for super admin."""
    api_client.force_authenticate(user=super_admin)
    response = api_client.get(
        path=reverse_lazy(
            "v1:super-admin:chamber-get-statistics",
            kwargs={"pk": chamber.pk},
        ),
        data={"year": 2023},
    )
    assert response.status_code == status.HTTP_200_OK


def test_super_admin_chamber_list_api(
    chambers: list[Chamber],
    deleted_chamber: Chamber,
    super_admin_client: APIClient,
):
    """Ensure super admin can get list of chambers."""
    response = super_admin_client.get(list_chamber_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == len(chambers)


def test_super_admin_chamber_detail_api(
    chamber: Chamber,
    super_admin_client: APIClient,
):
    """Ensure super admin can get detail of chamber."""
    _ = factories.ChamberBrandingFactory(chamber=chamber, chamber_logo=None)
    response = super_admin_client.get(
        detail_chamber_url(kwargs={"pk": chamber.pk}),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["branding"]["chamber_logo"] is None


def test_chamber_statistics_year_filtering_api(
    api_client: APIClient,
    super_admin: User,
    chamber: Chamber,
) -> None:
    """Ensure chamber statistic API with year filter work for super admin."""
    api_client.force_authenticate(user=super_admin)
    response = api_client.get(
        path=reverse_lazy(
            "v1:super-admin:chamber-get-statistics",
            kwargs={"pk": chamber.pk},
        ),
        data={"year": 2023},
    )
    assert response.status_code == status.HTTP_200_OK


def test_chamber_statistics_api_for_invalid_year(
    api_client: APIClient,
    super_admin: User,
    chamber: Chamber,
) -> None:
    """Ensure that the API return 404 for invalid year."""
    api_client.force_authenticate(user=super_admin)
    response = api_client.get(
        path=reverse_lazy(
            "v1:super-admin:chamber-get-statistics",
            kwargs={"pk": chamber.pk},
        ),
        data={"year": datetime.now().year - 4},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 0


def test_chamber_statistics_api_for_non_super_admin(
    api_client: APIClient,
    chamber_admin: User,
    chamber: Chamber,
) -> None:
    """Ensure chamber statistic API does not work for non-super admin."""
    api_client.force_authenticate(user=chamber_admin)
    response = api_client.get(
        path=reverse_lazy(
            "v1:super-admin:chamber-get-statistics",
            kwargs={"pk": chamber.pk},
        ),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_chamber_create_minimal_data(
    super_admin_client: APIClient,
    django_capture_on_commit_callbacks,
    mailoutbox,
):
    """Ensure super admin can create chamber with minimal data."""
    chamber_subdomain = "chamber1"
    trc_coord_email = "nygtrc@gmail.com"
    assert not Chamber.objects.filter(subdomain=chamber_subdomain).exists()
    assert not User.objects.filter(email=trc_coord_email).exists()
    minimal_data = {
        "name": "NYC",
        "nickname": "NYC & YGM",
        "subdomain": chamber_subdomain,
        "trc_coord_email": "nygtrc@gmail.com",
        "trc_coord_first_name": "first",
        "trc_coord_last_name": "last",
        "trc_coord_phone": "12345678910",
        "trc_coord_title": "PhD",
    }
    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        response = super_admin_client.post(
            list_chamber_url,
            data=minimal_data,
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert Chamber.objects.filter(subdomain=chamber_subdomain).exists()
    assert User.objects.filter(
        email=trc_coord_email,
        first_name=minimal_data["trc_coord_first_name"],
        last_name=minimal_data["trc_coord_last_name"],
        mobile_phone=minimal_data["trc_coord_phone"],
        chamber_id=response.data["id"],
    ).exists()
    assert ChamberBranding.objects.filter(
        chamber_id=response.data["id"],
    ).exists()
    assert "branding" in response.data
    assert len(callbacks) == 1
    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.to == [response.data["trc_coord_email"]]

    new_minimal_data = minimal_data.update({"name": "NYM"})
    another_response = super_admin_client.post(
        list_chamber_url,
        data=new_minimal_data,
    )
    assert another_response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    ["chamber_subdomain", "status_code"],
    [
        ["chamber1", status.HTTP_201_CREATED],
        ["123chamber", status.HTTP_201_CREATED],
        ["chamber-1", status.HTTP_201_CREATED],
        ["-chamber-1", status.HTTP_400_BAD_REQUEST],
        ["chamber-1-", status.HTTP_400_BAD_REQUEST],
        ["".join(["a"] * 64), status.HTTP_400_BAD_REQUEST],
    ],
)
def test_chamber_create_minimal_data_fail(
    super_admin_client: APIClient,
    chamber_subdomain: str,
    status_code: int,
    django_capture_on_commit_callbacks,
    mailoutbox,
):
    """Ensure chamber subdomain must pass all business validation.

    Business validation for chamber subdomain includes:
        - Each subdomain part must have length less than 64.
        - Each subdomain part must begin and end with an alpha numberic (i.e.
        letters [A-Za-z] or digits [0-9]).
        - Each subdomain part may contain hyphens but cannot begin or end with
        a hyphen.

    """
    trc_coord_email = "nygtrc@gmail.com"
    assert not Chamber.objects.filter(subdomain=chamber_subdomain).exists()
    assert not User.objects.filter(email=trc_coord_email).exists()
    minimal_data = {
        "name": "NYC",
        "nickname": "NYC & YGM",
        "subdomain": chamber_subdomain,
        "trc_coord_email": "nygtrc@gmail.com",
        "trc_coord_first_name": "first",
        "trc_coord_last_name": "last",
        "trc_coord_phone": "12345678910",
        "trc_coord_title": "PhD",
    }

    response = super_admin_client.post(
        list_chamber_url,
        data=minimal_data,
    )
    assert response.status_code == status_code


def test_chamber_create_full_data(
    super_admin_client: APIClient,
    django_capture_on_commit_callbacks,
    mailoutbox,
):
    """Ensure super admin can create chamber with full data."""
    chamber_data = factory.build(dict, FACTORY_CLASS=factories.ChamberFactory)
    branding_data = factory.build(
        dict,
        FACTORY_CLASS=factories.ChamberBrandingFactory,
    )
    branding_data.pop("chamber")
    chamber_data["branding"] = branding_data
    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        response = super_admin_client.post(
            list_chamber_url,
            data=chamber_data,
        )
    chamber_admins = User.objects.filter(
        role=UserRole.CHAMBER_ADMIN,
        chamber_id=response.data["id"],
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert len(chamber_admins) == 2
    assert (
        set(admin.email for admin in chamber_admins)
        == {chamber_data["trc_coord_email"], chamber_data["ceo_email"]}
    )
    assert "branding" in response.data
    assert len(callbacks) == 2
    assert len(mailoutbox) == 2
    mails_to = [mail.to for mail in mailoutbox]
    assert [chamber_data["trc_coord_email"]] in mails_to
    assert [chamber_data["ceo_email"]] in mails_to


def test_chamber_create_full_data_ceo_same_as_trc(
    super_admin_client: APIClient,
    django_capture_on_commit_callbacks,
    mailoutbox,
):
    """Ensure ceo admin isn't created if CEO info is the same as coord info."""
    chamber_data = factory.build(dict, FACTORY_CLASS=factories.ChamberFactory)
    chamber_data["ceo_email"] = chamber_data["trc_coord_email"]
    chamber_data["ceo_first_name"] = chamber_data["trc_coord_first_name"]
    chamber_data["ceo_last_name"] = chamber_data["trc_coord_last_name"]
    chamber_data["ceo_phone"] = chamber_data["trc_coord_phone"]
    branding_data = factory.build(
        dict,
        FACTORY_CLASS=factories.ChamberBrandingFactory,
    )
    branding_data.pop("chamber")
    chamber_data["branding"] = branding_data
    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        response = super_admin_client.post(
            list_chamber_url,
            data=chamber_data,
        )
    assert response.status_code == status.HTTP_201_CREATED, response.data
    chamber_admins = User.objects.filter(
        role=UserRole.CHAMBER_ADMIN,
        chamber_id=response.data["id"],
    )
    assert len(chamber_admins) == 1
    assert (
        set(admin.email for admin in chamber_admins)
        == {chamber_data["trc_coord_email"]}
    )
    assert "branding" in response.data
    assert len(callbacks) == 1
    assert len(mailoutbox) == 1
    mails_to = [mail.to for mail in mailoutbox]
    assert [chamber_data["trc_coord_email"]] in mails_to


def test_chamber_create_with_no_ceo_info(
    super_admin_client: APIClient,
    django_capture_on_commit_callbacks,
    mailoutbox,
):
    """Ensure super admin can create chamber with full data."""
    chamber_data = factory.build(dict, FACTORY_CLASS=factories.ChamberFactory)
    ceo_fields = (
        "ceo_email",
        "ceo_first_name",
        "ceo_last_name",
        "ceo_phone",
    )
    for field in ceo_fields:
        chamber_data.pop(field, None)

    branding_data = factory.build(
        dict,
        FACTORY_CLASS=factories.ChamberBrandingFactory,
    )
    branding_data.pop("chamber")
    chamber_data["branding"] = branding_data
    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        response = super_admin_client.post(
            list_chamber_url,
            data=chamber_data,
        )
    chamber_admins = User.objects.filter(
        role=UserRole.CHAMBER_ADMIN,
        chamber_id=response.data["id"],
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert len(chamber_admins) == 1
    assert chamber_admins[0].email == chamber_data["trc_coord_email"]
    assert "branding" in response.data
    assert len(callbacks) == 1
    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.to == [chamber_data["trc_coord_email"]]


def test_super_admin_update_chamber(
    django_db_blocker,
    super_admin_client: APIClient,
    chamber: Chamber,
):
    """Ensure super admin can update chamber with limited fields."""
    new_trc_first_name = chamber.trc_coord_first_name + "name"
    new_trc_last_name = chamber.trc_coord_last_name + "name"
    old_trc_email = chamber.trc_coord_email
    old_member_count = chamber.member_count
    chamber_update_data = {
        "trc_coord_first_name": new_trc_first_name,
        "trc_coord_last_name": new_trc_last_name,
        "trc_coord_email": "new" + chamber.trc_coord_email,
        "member_count": chamber.member_count,
        "subdomain": chamber.subdomain,
    }
    with django_db_blocker.unblock():
        chamber_admin = UserFactory(
            chamber=chamber,
            first_name=chamber.trc_coord_first_name,
            last_name=chamber.trc_coord_last_name,
            mobile_phone=chamber.trc_coord_phone,
            email=chamber.trc_coord_email,
            role=UserRole.CHAMBER_ADMIN,
        )

        response = super_admin_client.put(
            detail_chamber_url(kwargs={"pk": chamber.pk}),
            data=chamber_update_data,
        )
    assert response.status_code == status.HTTP_200_OK
    chamber.refresh_from_db()
    assert chamber.trc_coord_first_name == new_trc_first_name
    assert chamber.trc_coord_last_name == new_trc_last_name
    assert chamber.member_count == old_member_count
    assert chamber.trc_coord_email == old_trc_email
    chamber_admin.refresh_from_db()
    assert chamber_admin.first_name == new_trc_first_name
    assert chamber_admin.last_name == new_trc_last_name
    assert chamber_admin.email == old_trc_email


def test_super_admin_delete_chamber_api_incorrect_password(
    super_admin_client: APIClient,
    chamber: Chamber,
):
    """Ensure super admin can't delete chamber using incorrect password."""
    response = super_admin_client.post(
        get_chamber_url("delete", kwargs={"pk": chamber.pk}),
        data={
            "password": DEFAULT_PASSWORD + "!",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    chamber.refresh_from_db()
    assert chamber.deleted_at is None


def test_super_admin_delete_chamber_api_correct_password(
    super_admin_client: APIClient,
    chamber: Chamber,
):
    """Ensure super admin can delete chamber using correct password."""
    assert chamber.deleted_at is None
    response = super_admin_client.post(
        get_chamber_url("delete", kwargs={"pk": chamber.pk}),
        data={
            "password": DEFAULT_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    chamber.refresh_from_db()
    assert chamber.deleted_at is not None


def test_chamber_dashboard_api(
    chamber_admin: User,
    api_client: APIClient,
) -> None:
    """Ensure chamber admin can access dashboard API."""
    api_client.force_authenticate(user=chamber_admin)
    response = api_client.get(reverse_lazy("v1:chamber:dashboard"))
    assert response.status_code == status.HTTP_200_OK


def test_chamber_dashboard_api_for_non_chamber_admin(
    api_client: APIClient,
) -> None:
    """Ensure non-chamber admin can't access dashboard API."""
    api_client.force_authenticate(user=UserFactory())
    response = api_client.get(reverse_lazy("v1:chamber:dashboard"))
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_chamber_admin_update_api(
    api_client: APIClient,
    chamber_admin: User,
    other_chamber: Chamber,
) -> None:
    """Ensure chamber admin can update chamber."""
    data = {
        "address": "132, My Street",
        "city": "Kingston",
        "state": "NY",
        "zipcode": "12401",
        "country": "US",
        "phone": "+1 123 456 7890",
        "member_count": 100,
        "city_population": 100000,
        "country_population": 1000000,
        "msa_population": 10000000,
        "total_budget": 10000000,
        "total_membership_budget": 1000000,
        "pre_income": 50000,
        "ceo_first_name": "John",
        "ceo_last_name": "Doe",
        "ceo_email": "john.doe@gmail.com",
        "ceo_phone": "+1 123 456 7890",
    }
    chamber_admin.chamber = other_chamber
    UserFactory(
        role=UserRole.CHAMBER_ADMIN,
        chamber=other_chamber,
        email=other_chamber.ceo_email,
    )
    api_client.force_authenticate(user=chamber_admin)
    url = reverse("v1:chamber:info")
    api_client.force_authenticate(
        user=chamber_admin,
        token=AuthToken.objects.create(chamber_admin)[0],
    )
    response = api_client.put(
        url,
        data=data,
    )
    assert response.status_code == status.HTTP_200_OK
    other_chamber.refresh_from_db()

    for key, value in data.items():
        if key.startswith("ceo_"):
            assert getattr(other_chamber, key) != value
            continue
        assert getattr(other_chamber, key) == value


def test_coord_admin_create_ceo_admin_on_chamber_update(
    api_client: APIClient,
    django_capture_on_commit_callbacks,
    mailoutbox,
):
    """Ensure TRC coord admin can create new CEO admin."""
    chamber_data = factory.build(
        dict,
        FACTORY_CLASS=factories.ChamberFactory,
        ceo_email="",
        ceo_first_name="",
        ceo_last_name="",
        ceo_phone="",
    )
    _chamber = Chamber.objects.create(**chamber_data)
    trc_coord_admin = UserFactory(
        role=UserRole.CHAMBER_ADMIN,
        email=_chamber.trc_coord_email,
        chamber=_chamber,
    )
    assert _chamber.users.filter(role=UserRole.CHAMBER_ADMIN).count() == 1
    api_client.force_authenticate(
        trc_coord_admin,
        token=AuthToken.objects.create(trc_coord_admin)[0],
    )
    chamber_data["ceo_email"] = "a" + _chamber.trc_coord_email
    chamber_data["ceo_first_name"] = "first"
    chamber_data["ceo_last_name"] = "last"
    chamber_data["ceo_phone"] = "1234567890"
    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        response = api_client.put(
            reverse("v1:chamber:info"),
            data=chamber_data,
        )
    assert response.status_code == status.HTTP_200_OK, response.data
    assert _chamber.users.filter(role=UserRole.CHAMBER_ADMIN).count() == 2
    assert _chamber.users.filter(
        role=UserRole.CHAMBER_ADMIN,
        email=chamber_data["ceo_email"],
    ).exists()
    assert len(callbacks) == 1
    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.to == [chamber_data["ceo_email"]]


def test_coord_admin_dont_create_ceo_admin_on_chamber_update(
    api_client: APIClient,
    django_capture_on_commit_callbacks,
    mailoutbox,
):
    """Ensure TRC coord admin don't create new CEO admin."""
    chamber_data = factory.build(
        dict,
        FACTORY_CLASS=factories.ChamberFactory,
        ceo_email="",
        ceo_first_name="",
        ceo_last_name="",
        ceo_phone="",
    )
    _chamber = Chamber.objects.create(**chamber_data)
    trc_coord_admin = UserFactory(
        role=UserRole.CHAMBER_ADMIN,
        email=_chamber.trc_coord_email,
        chamber=_chamber,
    )
    assert _chamber.users.filter(role=UserRole.CHAMBER_ADMIN).count() == 1
    api_client.force_authenticate(
        trc_coord_admin,
        token=AuthToken.objects.create(trc_coord_admin)[0],
    )
    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        response = api_client.put(
            reverse("v1:chamber:info"),
            data=chamber_data,
        )
    assert response.status_code == status.HTTP_200_OK, response.data
    assert _chamber.users.filter(role=UserRole.CHAMBER_ADMIN).count() == 1
    assert not _chamber.users.filter(
        role=UserRole.CHAMBER_ADMIN,
        email=chamber_data["ceo_email"],
    ).exists()
    assert len(callbacks) == 0
    assert len(mailoutbox) == 0


def test_update_existing_ceo_admin_on_chamber_update(
    api_client: APIClient,
    django_capture_on_commit_callbacks,
    mailoutbox,
):
    """Ensure coord admin can't update existing CEO's admin."""
    chamber_data = factory.build(
        dict,
        FACTORY_CLASS=factories.ChamberFactory,
    )
    _chamber = Chamber.objects.create(**chamber_data)
    trc_coord_admin = UserFactory(
        role=UserRole.CHAMBER_ADMIN,
        email=_chamber.trc_coord_email,
        chamber=_chamber,
    )
    existing_ceo_admin: User = UserFactory(
        role=UserRole.CHAMBER_ADMIN,
        email=_chamber.ceo_email,
        chamber=_chamber,
        first_name=_chamber.ceo_first_name,
        last_name=_chamber.ceo_last_name,
        mobile_phone=_chamber.ceo_phone,
    )
    assert _chamber.users.filter(role=UserRole.CHAMBER_ADMIN).count() == 2
    api_client.force_authenticate(
        trc_coord_admin,
        token=AuthToken.objects.create(trc_coord_admin)[0],
    )
    chamber_data["ceo_email"] = "a" + chamber_data["ceo_email"]
    chamber_data["ceo_first_name"] = "first" + chamber_data["ceo_first_name"]
    chamber_data["ceo_last_name"] = "last" + chamber_data["ceo_last_name"]
    chamber_data["ceo_phone"] = "1234567890"
    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        response = api_client.put(
            reverse("v1:chamber:info"),
            data=chamber_data,
        )
    assert response.status_code == status.HTTP_200_OK, response.data
    existing_ceo_admin.refresh_from_db()
    assert existing_ceo_admin.email != chamber_data["ceo_email"]
    assert existing_ceo_admin.first_name != chamber_data["ceo_first_name"]
    assert existing_ceo_admin.last_name != chamber_data["ceo_last_name"]
    assert existing_ceo_admin.mobile_phone != chamber_data["ceo_phone"]
    assert len(callbacks) == 0
    assert len(mailoutbox) == 0


def test_chamber_admin_update_api_with_non_chamber_admin(
    api_client: APIClient,
    other_chamber: Chamber,
) -> None:
    """Ensure that non chamber admin can't update chamber."""
    user = UserFactory()
    api_client.force_authenticate(user=user)
    url = reverse("v1:chamber:info")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_super_admin_impersonate_update_chamber_api(
    api_client: APIClient,
    super_admin: User,
    chamber_admin: User,
    other_chamber: Chamber,
) -> None:
    """Ensure chamber admin can update chamber."""
    data = {
        "address": "132, My Street",
        "city": "Kingston",
        "state": "NY",
        "zipcode": "12401",
        "country": "US",
        "phone": "+1 123 456 7890",
        "member_count": 100,
        "city_population": 100000,
        "country_population": 1000000,
        "msa_population": 10000000,
        "total_budget": 10000000,
        "total_membership_budget": 1000000,
        "pre_income": 50000,
        "ceo_first_name": "John",
        "ceo_last_name": "Doe",
        "ceo_email": "john.doe@gmail.com",
        "ceo_phone": "+1 123 456 7890",
        "trc_coord_first_name": "first",
        "trc_coord_last_name": "last",
        "trc_coord_phone": "12345678910",
        "trc_coord_office_phone_ext": "11",
        "trc_coord_office_phone": "1111678910",
        "trc_coord_title": "PhD",
    }
    old_ceo_email = other_chamber.ceo_email
    chamber_admin.chamber = other_chamber
    chamber_admin.email = other_chamber.trc_coord_email
    chamber_admin.save()
    api_client.force_authenticate(
        user=chamber_admin,
        token=AuthToken.objects.create(super_admin)[0],
    )
    url = reverse("v1:chamber:info")
    response = api_client.put(
        url,
        data=data,
        headers={
            "chamber": other_chamber.id,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    other_chamber.refresh_from_db()

    for key, value in data.items():
        if key == "ceo_email":
            assert getattr(other_chamber, key) == old_ceo_email
            continue
        assert getattr(other_chamber, key) == value


@pytest.mark.parametrize(
    argnames=["user", "expected_status"],
    argvalues=[
        [pytest.lazy_fixture("super_admin"), status.HTTP_200_OK],
        [pytest.lazy_fixture("chamber_admin"), status.HTTP_403_FORBIDDEN],
    ],
)
def test_chamber_update_subdomain_api(
    api_client: APIClient,
    user: User,
    chamber: Chamber,
    expected_status: int,
) -> None:
    """Ensure only SA can update chamber's subdomain."""
    api_client.force_authenticate(user)
    UserFactory(
        chamber=chamber,
        role=UserRole.CHAMBER_ADMIN,
        email=chamber.trc_coord_email,
    )
    response = api_client.put(
        detail_chamber_url(kwargs={"pk": chamber.pk}),
        data={
            "subdomain": f"new_{chamber.subdomain}",
        },
    )
    assert response.status_code == expected_status


def test_chamber_update_subdomain_api_fail(
    api_client: APIClient,
    super_admin: User,
    chamber: Chamber,
    other_chamber: Chamber,
    live_campaign: Campaign,
) -> None:
    """Ensure SA cannot update subdomain in some circumstances.

    SA cannot update subdomain of chamber if:
        - Chamber is having a live campaign.
        - New subdomain already exists in other chamber.

    """
    api_client.force_authenticate(super_admin)
    UserFactory(chamber=chamber, role=UserRole.CHAMBER_ADMIN)
    response = api_client.put(
        detail_chamber_url(kwargs={"pk": chamber.pk}),
        data={
            "subdomain": f"new_{chamber.subdomain}",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response = api_client.put(
        detail_chamber_url(kwargs={"pk": chamber.pk}),
        data={
            "subdomain": other_chamber.subdomain,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_volunteer_validate_subdomain_api_sucess(
    chamber: Chamber,
    api_client: APIClient,
) -> None:
    """Ensure API returns id of validated subdomain in volunteer site."""
    CampaignFactory.create(chamber=chamber, status=CampaignStatus.LIVE)
    response = api_client.get(
        reverse_lazy("v1:chamber-subdomain-existence"),
        data={"subdomain": chamber.subdomain},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["chamber"]["id"] == chamber.pk


def test_volunteer_validate_subdomain_api_fail(
    chamber: Chamber,
    api_client: APIClient,
) -> None:
    """Ensure API raises error when providing non-exist subdomain for VS."""
    invalid_subdomain = f"invalid_{chamber.subdomain}"
    response = api_client.get(
        reverse_lazy("v1:chamber-subdomain-existence"),
        data={"subdomain": invalid_subdomain},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_renew_chamber_campaign_fail_active_campaign(
    api_client: APIClient,
    super_admin: User,
    chamber: Chamber,
    live_campaign: Campaign,
    renew_chamber_campaign_config: dict,
) -> None:
    """Ensure chamber still contains active campaign cannot be renewed."""
    api_client.force_authenticate(super_admin)
    response = api_client.post(
        renew_chamber_campaign_url(kwargs={"pk": chamber.pk}),
        data=renew_chamber_campaign_config,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_renew_chamber_campaign_without_campaign(
    api_client: APIClient,
    super_admin: User,
    chamber: Chamber,
    renew_chamber_campaign_config: dict,
) -> None:
    """Ensure chamber without any campaigns can't be renewed."""
    api_client.force_authenticate(super_admin)
    response = api_client.post(
        renew_chamber_campaign_url(kwargs={"pk": chamber.pk}),
        data=renew_chamber_campaign_config,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# pylint: disable=too-many-arguments, too-many-locals
def test_renew_chamber_campaign_success_all_config(
    api_client: APIClient,
    super_admin: User,
    chamber: Chamber,
    completed_campaign: Campaign,
    renew_chamber_campaign_config: dict,
    product_categories: list[ProductCategory],
    chamber_full_campaign_data_for_renew,
) -> None:
    """Ensure chamber with all done campaigns can renew successfully."""
    api_client.force_authenticate(super_admin)
    response = api_client.post(
        renew_chamber_campaign_url(kwargs={"pk": chamber.pk}),
        data=renew_chamber_campaign_config,
    )
    campaign_renew_name_list = (
        completed_campaign.name,
        renew_chamber_campaign_config["name"],
    )
    assert response.status_code == status.HTTP_200_OK, response.data
    assert Campaign.objects.filter(
        name__in=campaign_renew_name_list,
        chamber=completed_campaign.chamber,
    ).count() == 2
    for category in product_categories:
        assert ProductCategory.objects.filter(name=category.name).count() == 2
        assert Product.objects.filter(
            category__name=category.name,
        ).count() == 4
        assert Level.objects.filter(
            product__category__name=category.name,
        ).count() == 8
        assert LevelInstance.objects.filter(
            level__product__category__name=category.name,
        ).count() == 16
    incentives = Incentive.objects.filter(campaign=completed_campaign)
    for incentive in incentives:
        assert Incentive.objects.filter(name=incentive.name).count() == 2
        assert IncentiveQualifier.objects.filter(
            incentive__name=incentive.name,
        ).count() == 4
    teams = Team.objects.filter(campaign=completed_campaign)
    for team in teams:
        assert Team.objects.filter(name=team.name).count() == 2
        assert UserCampaign.objects.filter(team__name=team.name).count() == 4
    users = UserCampaign.objects.filter(
        campaign=completed_campaign,
        team__in=teams,
    )
    for user in users:
        contracts = Contract.objects.filter(created_by__email=user.email)
        assert contracts.count() == 4
    renew_campaign = Campaign.objects.filter(
        name__in=campaign_renew_name_list,
        chamber=completed_campaign.chamber,
    ).exclude(id=completed_campaign.pk).first()
    contracts = renew_campaign.contracts.all()
    assert LevelInstance.objects.filter(
        level__product__category__campaign=renew_campaign,
        contract__in=contracts,
    ).count() == 16
