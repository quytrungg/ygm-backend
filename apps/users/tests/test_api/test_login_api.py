from django.urls import reverse_lazy

from rest_framework import status, test
from rest_framework.response import Response

import pytest

from apps.campaigns.constants import CampaignStatus
from apps.campaigns.factories import CampaignFactory, UserCampaignFactory
from apps.chambers.factories import ChamberFactory
from apps.chambers.models import Chamber
from apps.users import factories, models


def get_login_url(basename: str, kwargs=None):
    """Return url for super admin chamber api."""
    return reverse_lazy(f"v1:{basename}:login", kwargs=kwargs)


super_admin_login_url = get_login_url(basename="super-admin")
chamber_admin_login_url = get_login_url(basename="chamber")
volunteer_login_url = get_login_url(basename="volunteer")


def test_super_admin_login_success(
    api_client: test.APIClient,
    super_admin: models.User,
) -> None:
    """Ensure super admin can login."""
    response: Response = api_client.post(
        path=super_admin_login_url,
        data={
            "email": super_admin.email,
            "password": factories.DEFAULT_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_200_OK


def test_super_admin_login_fail(
    api_client: test.APIClient,
    chamber_admin: models.User,
) -> None:
    """Ensure non-super admin cannot login."""
    response: Response = api_client.post(
        path=super_admin_login_url,
        data={
            "email": chamber_admin.email,
            "password": factories.DEFAULT_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_chamber_admin_login_success(
    api_client: test.APIClient,
    chamber_admin: models.User,
) -> None:
    """Ensure chamber admin can login with chamber information."""
    response = api_client.post(
        path=chamber_admin_login_url,
        data={
            "email": chamber_admin.email,
            "password": factories.DEFAULT_PASSWORD,
            "chamber_id": chamber_admin.chamber_id,
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.data


def test_chamber_admin_login_fail(
    api_client: test.APIClient,
    chamber: Chamber,
) -> None:
    """Ensure non-chamber admin cannot login using chamber admin path."""
    normal_user = factories.UserFactory(chamber=chamber)
    response = api_client.post(
        path=chamber_admin_login_url,
        data={
            "email": normal_user.email,
            "password": factories.DEFAULT_PASSWORD,
            "chamber_id": chamber.id,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    argnames="user",
    argvalues=[
        pytest.lazy_fixture("volunteer"),
        pytest.lazy_fixture("chamber_admin"),
    ],
)
def test_volunteer_login_success(
    api_client: test.APIClient,
    user: models.User,
    chamber: Chamber,
) -> None:
    """Ensure volunteer can login using volunteer login url."""
    user.chamber = chamber
    user.save()
    campaign = CampaignFactory(chamber=chamber, status=CampaignStatus.LIVE)
    UserCampaignFactory(user=user, campaign=campaign)
    response = api_client.post(
        path=volunteer_login_url,
        data={
            "email": user.email,
            "password": factories.DEFAULT_PASSWORD,
            "chamber_id": chamber.pk,
        },
    )
    assert response.status_code == status.HTTP_200_OK


def test_volunteer_login_success_with_open_campaign(
    volunteer: models.User,
    api_client: test.APIClient,
    chamber: Chamber,
) -> None:
    """Ensure volunteers can login with open campaign."""
    volunteer.chamber = chamber
    volunteer.save()
    campaign = CampaignFactory(chamber=chamber, status=CampaignStatus.CREATED)
    UserCampaignFactory(user=volunteer, campaign=campaign)
    response = api_client.post(
        path=volunteer_login_url,
        data={
            "email": volunteer.email,
            "password": factories.DEFAULT_PASSWORD,
            "chamber_id": chamber.pk,
        },
    )
    assert response.status_code == status.HTTP_200_OK


def test_volunteer_login_non_existed_user(api_client: test.APIClient) -> None:
    """Ensure unregistered users cannot login to volunteer site."""
    response = api_client.post(
        path=volunteer_login_url,
        data={
            "email": "test@gmail.com",
            "password": factories.DEFAULT_PASSWORD,
            "chamber_id": "",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_volunteer_login_mismatched_chamber(
    volunteer: models.User,
    api_client: test.APIClient,
    chamber: Chamber,
) -> None:
    """Ensure volunteers with different chamber cannot login."""
    volunteer.chamber = ChamberFactory()
    volunteer.save()
    response = api_client.post(
        path=volunteer_login_url,
        data={
            "email": "test@gmail.com",
            "password": factories.DEFAULT_PASSWORD,
            "chamber_id": chamber.pk,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_volunteer_login_invalid_user_campaign(
    volunteer: models.User,
    api_client: test.APIClient,
    chamber: Chamber,
) -> None:
    """Ensure volunteers can't login if not invited to join campaign."""
    volunteer.chamber = chamber
    volunteer.save()
    campaign = CampaignFactory(chamber=chamber, status=CampaignStatus.DONE)
    # user campaign for last campaign, not invite to current live campaign yet
    UserCampaignFactory(user=volunteer, campaign=campaign)
    CampaignFactory(chamber=chamber, status=CampaignStatus.LIVE)
    response = api_client.post(
        path=volunteer_login_url,
        data={
            "email": volunteer.email,
            "password": factories.DEFAULT_PASSWORD,
            "chamber_id": chamber.pk,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
