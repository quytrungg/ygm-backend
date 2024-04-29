from django.urls import reverse_lazy
from django.utils import timezone

from rest_framework import status, test

import pytest
from safedelete import HARD_DELETE

from apps.campaigns.factories import CampaignFactory, UserCampaignFactory
from apps.campaigns.models import Campaign
from apps.campaigns.notifications import VolunteerInvitationEmailNotification
from apps.chambers.factories import ChamberFactory
from apps.chambers.notifications import WelcomeChamberAdminEmailNotification

from ... import factories, models
from ...constants import UserRole

chamber_admin_register_url = reverse_lazy("v1:chamber:register")
volunteer_register_url = reverse_lazy("v1:volunteer:register")


@pytest.fixture(scope="module")
def unregistered_chamber_admin(django_db_blocker) -> models.User:
    """Return an existing unregistered chamber admin."""
    with django_db_blocker.unblock():
        chamber = ChamberFactory()
        chamber_admin = factories.UserFactory.build(
            role=UserRole.CHAMBER_ADMIN,
            chamber=chamber,
            email=chamber.trc_coord_email,
        )
        chamber_admin.set_unusable_password()
        chamber_admin.save()
        yield chamber_admin
        chamber_admin.delete(force_policy=HARD_DELETE)
        chamber.delete(force_policy=HARD_DELETE)


@pytest.fixture(scope="module")
def chamber_admin_registration_tokens(
    unregistered_chamber_admin: models.User,
) -> dict:
    """Return the creds included in registration url."""
    mail = WelcomeChamberAdminEmailNotification(unregistered_chamber_admin)
    mail_ctx = mail.get_template_context()
    return {
        "uid": mail_ctx["uid"],
        "token": mail_ctx["token"],
        "chamber_id": unregistered_chamber_admin.chamber_id,
    }


def test_chamber_admin_register_successful(
    api_client: test.APIClient,
    chamber_admin_registration_tokens: dict,
):
    """Ensure chamber admin can register successfully."""
    response = api_client.post(
        chamber_admin_register_url,
        data={
            "password": factories.DEFAULT_PASSWORD,
            "password_confirm": factories.DEFAULT_PASSWORD,
            **chamber_admin_registration_tokens,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["token"]


def test_chamber_admin_register_with_volunteer_api(
    api_client: test.APIClient,
    chamber_admin_registration_tokens: dict,
):
    """Ensure chamber admin can't register using volunteer register API."""
    response = api_client.post(
        volunteer_register_url,
        data={
            "password": factories.DEFAULT_PASSWORD,
            "password_confirm": factories.DEFAULT_PASSWORD,
            **chamber_admin_registration_tokens,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_chamber_admin_register_incorrect_token(
    api_client: test.APIClient,
    chamber_admin_registration_tokens: dict,
):
    """Ensure registration fails due to incorrect token."""
    response = api_client.post(
        chamber_admin_register_url,
        data={
            "password": factories.DEFAULT_PASSWORD,
            "password_confirm": factories.DEFAULT_PASSWORD,
            "uid": chamber_admin_registration_tokens["uid"],
            "token": chamber_admin_registration_tokens["token"] + "s",
            "chamber_id": chamber_admin_registration_tokens["chamber_id"],
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["errors"][0]["attr"] == "token"


def test_chamber_admin_register_mismatch_password(
    api_client: test.APIClient,
    chamber_admin_registration_tokens: dict,
):
    """Ensure registration fails due to mismatched password."""
    response = api_client.post(
        chamber_admin_register_url,
        data={
            "password": factories.DEFAULT_PASSWORD,
            "password_confirm": factories.DEFAULT_PASSWORD + "s",
            **chamber_admin_registration_tokens,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["errors"][0]["attr"] == "password_confirm"


def test_chamber_admin_register_registered_account(
    api_client: test.APIClient,
):
    """Ensure registration fails due to using registered account's token."""
    chamber = ChamberFactory()
    chamber_admin = factories.UserFactory.build(
        role=UserRole.CHAMBER_ADMIN,
        chamber=chamber,
        email=chamber.trc_coord_email,
    )
    chamber_admin.last_login = timezone.now()
    chamber_admin.save()
    mail = WelcomeChamberAdminEmailNotification(chamber_admin)
    mail_ctx = mail.get_template_context()
    response = api_client.post(
        chamber_admin_register_url,
        data={
            "uid": mail_ctx["uid"],
            "token": mail_ctx["token"],
            "password": factories.DEFAULT_PASSWORD,
            "password_confirm": factories.DEFAULT_PASSWORD,
            "chamber_id": chamber.id,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["errors"][0]["attr"] == "uid", response.data


def test_chamber_admin_get_registration_info(
    unregistered_chamber_admin: models.User,
    chamber_admin_registration_tokens: dict,
    api_client: test.APIClient,
):
    """Ensure registration info can be retrieved with correct tokens."""
    url = reverse_lazy("v1:chamber:register-info")
    response = api_client.get(
        path=url,
        data=chamber_admin_registration_tokens,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data
    assert data["first_name"] == unregistered_chamber_admin.first_name
    assert data["last_name"] == unregistered_chamber_admin.last_name
    assert data["mobile_phone"] == unregistered_chamber_admin.mobile_phone
    assert data["email"] == unregistered_chamber_admin.email


# -----------------------------------------------------------------------------
# VS tests
# -----------------------------------------------------------------------------


@pytest.fixture
def active_campaign():
    """Return a live campaign."""
    return CampaignFactory(status=Campaign.STATUSES.LIVE)


@pytest.fixture
def open_campaign():
    """Return an open campaign."""
    return CampaignFactory(status=Campaign.STATUSES.CREATED)


def create_volunteer(campaign: Campaign):
    """Return a volunteer."""
    user = factories.UserFactory.build(
        role=UserRole.VOLUNTEER,
        chamber=campaign.chamber,
    )
    user.set_unusable_password()
    user.save()
    UserCampaignFactory(user=user, campaign=campaign)
    return user


def create_volunteer_registration_tokens(volunteer: models.User):
    """Return volunteer's registration tokens."""
    invitation_email = VolunteerInvitationEmailNotification(
        volunteer=volunteer,
        campaign=None,
    )
    mail_ctx = invitation_email.get_template_context()
    return {
        "uid": mail_ctx["uid"],
        "token": mail_ctx["token"],
    }


@pytest.mark.parametrize(
    argnames="campaign",
    argvalues=[
        pytest.lazy_fixture("open_campaign"),
        pytest.lazy_fixture("active_campaign"),
    ],
)
def test_volunteer_register_successful(
    api_client: test.APIClient,
    campaign: Campaign,
):
    """Ensure volunteer can register successfully."""
    volunteer = create_volunteer(campaign)
    registration_tokens = create_volunteer_registration_tokens(volunteer)
    response = api_client.post(
        volunteer_register_url,
        data={
            "password": factories.DEFAULT_PASSWORD,
            "password_confirm": factories.DEFAULT_PASSWORD,
            "chamber_id": campaign.chamber_id,
            **registration_tokens,
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.data
    assert response.data["token"]


def test_volunteer_get_registration_info(
    api_client: test.APIClient,
    active_campaign: Campaign,
):
    """Ensure registration info can be retrieved with correct tokens."""
    volunteer = create_volunteer(active_campaign)
    registration_tokens = create_volunteer_registration_tokens(volunteer)
    response = api_client.get(
        path=reverse_lazy("v1:volunteer:register-info"),
        data={
            "chamber_id": active_campaign.chamber_id,
            **registration_tokens,
        },
    )
    data = response.data
    assert response.status_code == status.HTTP_200_OK, data
    assert data["first_name"] == volunteer.first_name
    assert data["last_name"] == volunteer.last_name
    assert data["email"] == volunteer.email
