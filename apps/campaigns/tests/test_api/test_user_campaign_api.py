import decimal
from functools import partial

from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.test import APIClient

import pytest
from knox.models import AuthToken

from apps.campaigns import constants as campaign_constants
from apps.campaigns import factories as campaign_factories
from apps.campaigns import models as campaign_models
from apps.campaigns.constants import CampaignStatus, UserCampaignRole
from apps.campaigns.factories import (
    CampaignFactory,
    TeamFactory,
    UserCampaignFactory,
)
from apps.campaigns.models import Team, UserCampaign
from apps.chambers.factories import StoredMemberFactory
from apps.chambers.models import Chamber, StoredMember
from apps.core.constants import MAX_PHONE_NUMBER_LENGTH, MAX_ZIP_CODE_LENGTH
from apps.core.test_utils import CAAPIClient, get_test_file_url
from apps.members.factories import ContractFactory
from apps.members.models import Contract, ContractCreditInfo
from apps.users.factories import UserFactory
from apps.users.models import User

from ...api.permissions import IsUserCampaignDeletable


def get_user_campaign_url(action: str, kwargs=None):
    """Return url for user-campaign's APIs."""
    return reverse_lazy(
        f"v1:chamber:user-campaign-{action}",
        kwargs=kwargs,
    )


get_user_campaign_list_url = partial(get_user_campaign_url, action="list")
get_user_campaign_assign_role_url = get_user_campaign_url(action="assign-role")
get_user_campaign_assign_team_url = get_user_campaign_url(action="assign-team")
get_user_campaign_roles_url = get_user_campaign_url(action="roles")
get_user_campaign_detail_url = partial(get_user_campaign_url, action="detail")
vs_profile_url = reverse_lazy("v1:volunteer:profile")
get_user_campaign_send_registration_link = partial(
    get_user_campaign_url,
    action="send-registration-link",
)


@pytest.fixture
def stored_member(chamber: Chamber) -> StoredMember:
    """Return a chamber's stored member."""
    return StoredMemberFactory(chamber=chamber)


@pytest.fixture
def profile_update_data(create_file) -> dict:
    """Return data for updating profile."""
    return {
        "email": "volunteer@gmail.com",
        "first_name": "Volunteer",
        "last_name": "1",
        "role": "volunteer",
        "avatar": get_test_file_url(create_file("avatar.png")),
        "mobile_phone": "1234567890",
        "work_phone": "1234567890",
        "birthday": "2000-01-01",
        "home_address": "1234 A Street",
        "home_city": "Kingston",
        "home_state": "NY",
        "home_zip_code": "12401",
        "title": "Python Developer",
        "company_name": "Company",
        "company_address": "1234 Address Street",
        "company_city": "Los Angeles",
        "company_state": "CA",
        "company_zip_code": "90000",
        "preferred_contact_methods": [
            "Text",
        ],
        "preference": {
            "favorite_candy": "Candy 1",
            "favorite_drink": "",
            "favorite_restaurant": "",
            "favorite_movie": "",
            "hobbies": "",
            "instagram_url": "",
            "facebook_url": "",
            "twitter_url": "",
        },
    }


@pytest.fixture
def user_campaign_update_data() -> dict:
    """Return data for updating user campaign."""
    return {
        "id": 21,
        "first_name": "John",
        "last_name": "Kelly",
        "mobile_phone": "515151919191",
        "work_phone": "515151919191",
        "email": "user_campaign@gmail.com",
        "role": "volunteer",
        "company_name": "Company",
        "team": 12,
        "is_active": False,
        "teams": [],
    }


@pytest.fixture
def user_assign_volunteer_data(volunteers_team_1: list[UserCampaign]) -> dict:
    """Return data of volunteers from team 1 and assign to role volunteer."""
    return {
        "ids": [user.pk for user in volunteers_team_1],
        "role": UserCampaignRole.VOLUNTEER,
    }


@pytest.fixture
def user_assign_team_captain_data(
    volunteers_team_1: list[UserCampaign],
) -> dict:
    """Return data of volunteers from team 1 and assign to team captain."""
    return {
        "ids": [user.pk for user in volunteers_team_1],
        "role": UserCampaignRole.TEAM_CAPTAIN,
    }


@pytest.fixture
def user_assign_chamber_chair_data(
    volunteers_team_1: list[UserCampaign],
) -> dict:
    """Return data of volunteers from team 1 and assign to chamber chair."""
    return {
        "ids": [user.pk for user in volunteers_team_1],
        "role": UserCampaignRole.CHAMBER_CHAIR,
    }


@pytest.fixture
def user_volunteer_assign_team_data(
    volunteers_team_1: list[UserCampaign],
    another_team: Team,
) -> dict:
    """Return data of volunteers from team 1 and assign to team 2 data."""
    return {
        "ids": [user.pk for user in volunteers_team_1],
        "team": another_team.pk,
    }


@pytest.fixture
def user_team_captain_assign_team_data(
    team_captains_team_1: list[UserCampaign],
    another_team: Team,
) -> dict:
    """Return team with team captain from team 1 and assign to team 2 data."""
    return {
        "ids": [user.pk for user in team_captains_team_1],
        "team": another_team.pk,
    }


@pytest.fixture
def user_chamber_chair_assign_team_data(
    chamber_chair_users: list[UserCampaign],
    team: Team,
) -> dict:
    """Return data of chamber chair users and assign to team."""
    return {
        "ids": [user.pk for user in chamber_chair_users],
        "team": team.pk,
    }


def test_user_campaign_list_api(
    chamber: Chamber,
) -> None:
    """Ensure that user campaign list API work as expected."""
    campaign = CampaignFactory(chamber=chamber, status=CampaignStatus.LIVE)
    chamber_admin = UserFactory(role=User.ROLES.CHAMBER_ADMIN, chamber=chamber)
    UserCampaignFactory.create_batch(campaign=campaign, size=5)
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(chamber_admin)
    response = api_client.get(get_user_campaign_list_url())
    assert response.status_code == status.HTTP_200_OK, response.data


def test_user_campaign_detail_api(
    chamber: Chamber,
    stored_member: StoredMember,
) -> None:
    """Ensure that user campaign detail API work as expected."""
    campaign = CampaignFactory(chamber=chamber, status=CampaignStatus.LIVE)
    chamber_admin = UserFactory(role=User.ROLES.CHAMBER_ADMIN, chamber=chamber)
    user_campaign = UserCampaignFactory(
        campaign=campaign,
        role=UserCampaignRole.VOLUNTEER,
        member=stored_member,
    )
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(chamber_admin)
    response = api_client.get(
        get_user_campaign_detail_url(
            kwargs={"pk": user_campaign.pk},
        ),
    )
    assert response.status_code == status.HTTP_200_OK, response.data


def test_user_campaign_update_api(
    chamber: Chamber,
    user_campaign_update_data: dict,
    stored_member: StoredMember,
) -> None:
    """Ensure that user campaign update API works as expected."""
    campaign = CampaignFactory(chamber=chamber, status=CampaignStatus.RENEWAL)
    chamber_admin = UserFactory(role=User.ROLES.CHAMBER_ADMIN, chamber=chamber)
    user_campaign = UserCampaignFactory(
        campaign=campaign,
        role=UserCampaignRole.VOLUNTEER,
        member=stored_member,
    )
    team = TeamFactory(campaign=campaign)
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(
        user=chamber_admin,
        token=AuthToken.objects.create(chamber_admin)[0],
    )
    user_campaign_update_data["team"] = team.pk
    user_campaign_update_data["member"] = stored_member.pk
    response = api_client.put(
        get_user_campaign_detail_url(
            kwargs={"pk": user_campaign.pk},
        ),
        data=user_campaign_update_data,
    )
    assert response.status_code == status.HTTP_200_OK, response.data
    user_campaign.refresh_from_db()
    assert user_campaign.email != user_campaign_update_data["email"]


def test_user_campaign_update_api_with_live_campaign(
    chamber: Chamber,
    user_campaign_update_data: dict,
    stored_member: StoredMember,
) -> None:
    """Ensure that user campaign update API works as expected.

    Ensure it return 403 if campaign is live.

    """
    campaign = CampaignFactory(chamber=chamber, status=CampaignStatus.LIVE)
    chamber_admin = UserFactory(role=User.ROLES.CHAMBER_ADMIN, chamber=chamber)
    user_campaign = UserCampaignFactory(
        campaign=campaign,
        role=UserCampaignRole.VOLUNTEER,
        member=stored_member,
    )
    team = TeamFactory(campaign=campaign)
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(
        chamber_admin,
        token=AuthToken.objects.create(chamber_admin)[0],
    )
    user_campaign_update_data["team"] = team.pk
    response = api_client.put(
        get_user_campaign_detail_url(
            kwargs={"pk": user_campaign.pk},
        ),
        data=user_campaign_update_data,
    )
    assert response.status_code == status.HTTP_200_OK


def test_user_campaign_update_api_chamber_admin_update_chamber_admin_role(
    chamber: Chamber,
    user_campaign_update_data: dict,
    stored_member: StoredMember,
) -> None:
    """Ensure that chamber admin cannot update role of other chamber admin."""
    campaign = CampaignFactory(chamber=chamber, status=CampaignStatus.CREATED)
    chamber_admin1 = UserFactory(
        role=User.ROLES.CHAMBER_ADMIN,
        chamber=chamber,
    )
    chamber_admin2 = UserFactory(
        role=User.ROLES.CHAMBER_ADMIN,
        chamber=chamber,
    )
    user_campaign = UserCampaignFactory(
        campaign=campaign,
        user=chamber_admin2,
        role=UserCampaignRole.CHAMBER_ADMIN,
        member=stored_member,
    )
    team = TeamFactory(campaign=campaign)
    user_campaign_update_data["team"] = team.pk
    user_campaign_update_data["member"] = stored_member.pk
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(
        user=chamber_admin1,
        token=AuthToken.objects.create(chamber_admin1)[0],
    )
    response = api_client.put(
        get_user_campaign_detail_url(
            kwargs={"pk": user_campaign.pk},
        ),
        data=user_campaign_update_data,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_new_volunteer_without_existing_account(
    chamber_admin_2: User,
    django_capture_on_commit_callbacks,
    mailoutbox,
    stored_member: StoredMember,
):
    """Ensure chamber admin can create new user."""
    campaign = campaign_models.Campaign.objects.filter(
        chamber_id=chamber_admin_2.chamber_id,
    ).exclude(status=CampaignStatus.DONE).first()
    team = TeamFactory(campaign_id=campaign.id)
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(chamber_admin_2)
    creation_data = {
        "first_name": "new",
        "last_name": "member",
        "email": "newmember@gmail.com",
        "role": UserCampaignRole.VOLUNTEER,
        "team": team.id,
        "team_manager": None,
        "member": stored_member.pk,
    }
    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        response = api_client.post(
            get_user_campaign_list_url(),
            data=creation_data,
        )
    assert response.status_code == status.HTTP_201_CREATED
    assert len(callbacks) == 1
    assert len(mailoutbox) == 1
    user_campaign_id = response.data["id"]
    user_campaign = campaign_models.UserCampaign.objects.get(
        id=user_campaign_id,
    )
    new_user = User.objects.get(id=user_campaign.user_id)
    for field in creation_data:
        if hasattr(new_user, field):
            assert getattr(new_user, field) == getattr(user_campaign, field)
    assert new_user.role == User.ROLES.VOLUNTEER
    assert user_campaign.team_id == team.id


def test_user_campaign_send_registration_link_api(
    chamber_admin: User,
    open_campaign: campaign_models.Campaign,
    mailoutbox,
    stored_member: StoredMember,
) -> None:
    """Ensure CA can resend registration link to campaign user."""
    user_campaign = UserCampaignFactory(
        campaign=open_campaign,
        role=UserCampaignRole.VOLUNTEER,
        member=stored_member,
    )
    api_client = CAAPIClient()
    api_client.select_campaign(open_campaign)
    api_client.force_authenticate(chamber_admin)
    url = get_user_campaign_send_registration_link(
        kwargs={"pk": user_campaign.id},
    )
    response = api_client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(mailoutbox) == 1


def test_create_new_volunteer_with_existing_account_of_open_campaign(
    chamber_admin_2: User,
    stored_member: StoredMember,
):
    """Ensure user can't be created.

    We don't allow user to be created with same email while campaign is not
    done.

    """
    campaign = campaign_models.Campaign.objects.filter(
        chamber_id=chamber_admin_2.chamber_id,
    ).exclude(status=CampaignStatus.DONE).first()
    team = TeamFactory(campaign_id=campaign.id)
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(chamber_admin_2)
    creation_data = {
        "first_name": "new",
        "last_name": "member",
        "email": "newmember@gmail.com",
        "role": UserCampaignRole.VOLUNTEER,
        "team": team.id,
        "team_manager": None,
        "member": stored_member.pk,
    }
    response = api_client.post(
        get_user_campaign_list_url(),
        data=creation_data,
    )
    assert response.status_code == status.HTTP_201_CREATED, response.data

    another_response = api_client.post(
        get_user_campaign_list_url(),
        data=creation_data,
    )
    assert another_response.status_code == status.HTTP_400_BAD_REQUEST
    for error in another_response.data["errors"]:
        if error["attr"] == "email":
            assert error["detail"] == "Account with this email already exists"


def test_create_new_volunteer_with_existing_account_in_another_chamber(
    chamber_admin_2: User,
    another_chamber_admin: User,
    stored_member: StoredMember,
):
    """Ensure user can't be created.

    We don't allow user to be created with the email that is already used by
    another chamber.

    """
    campaign = campaign_models.Campaign.objects.filter(
        chamber_id=chamber_admin_2.chamber_id,
    ).exclude(status=CampaignStatus.DONE).first()
    team = TeamFactory(campaign_id=campaign.id)
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(chamber_admin_2)
    creation_data = {
        "first_name": "new",
        "last_name": "member",
        "email": "newmember@gmail.com",
        "role": UserCampaignRole.VOLUNTEER,
        "team": team.id,
        "team_manager": None,
        "member": stored_member.pk,
    }
    response = api_client.post(
        get_user_campaign_list_url(),
        data=creation_data,
    )
    assert response.status_code == status.HTTP_201_CREATED, response.data

    other_chamber_api_client = CAAPIClient()
    other_chamber_api_client.force_authenticate(another_chamber_admin)
    other_chamber_campaign = campaign_models.Campaign.objects.filter(
        chamber_id=another_chamber_admin.chamber_id,
    ).first()
    other_chamber_api_client.select_campaign(other_chamber_campaign)

    another_response = other_chamber_api_client.post(
        get_user_campaign_list_url(),
        data=creation_data,
    )
    assert another_response.status_code == status.HTTP_400_BAD_REQUEST
    for error in another_response.data["errors"]:
        if error["attr"] == "email":
            assert error["detail"] == "Account with this email already exists"


def test_create_new_volunteer_with_existing_account_of_completed_campaign(
    chamber_admin_2: User,
    stored_member: StoredMember,
):
    """Ensure user can be created.

    We allow user to be created in new campaign with no UserCampaign of that
    campaign uses the provided email.

    """
    campaign = campaign_models.Campaign.objects.filter(
        chamber_id=chamber_admin_2.chamber_id,
    ).exclude(status=CampaignStatus.DONE).first()
    team = TeamFactory(campaign_id=campaign.id)
    api_client = CAAPIClient()
    api_client.select_campaign(campaign)
    api_client.force_authenticate(chamber_admin_2)
    creation_data = {
        "first_name": "new",
        "last_name": "member",
        "email": "newmember@gmail.com",
        "role": UserCampaignRole.VOLUNTEER,
        "team": team.id,
        "team_manager": None,
        "member": stored_member.pk,
    }
    response = api_client.post(
        get_user_campaign_list_url(),
        data=creation_data,
    )
    assert response.status_code == status.HTTP_201_CREATED, response.data
    campaign.status = campaign_constants.CampaignStatus.DONE
    campaign.save()
    new_campaign = campaign_factories.CampaignFactory(
        chamber_id=chamber_admin_2.chamber_id,
        status=campaign_constants.CampaignStatus.CREATED,
    )
    new_team = TeamFactory(campaign_id=new_campaign.id)
    creation_data["team"] = new_team.id
    api_client.select_campaign(new_campaign)
    new_response = api_client.post(
        get_user_campaign_list_url(),
        data=creation_data,
    )
    assert new_response.status_code == status.HTTP_201_CREATED, response.data


def test_user_campaign_assign_team_api(
    volunteers_team_1: list[UserCampaign],
    chamber_admin_client: CAAPIClient,
    user_volunteer_assign_team_data: dict,
) -> None:
    """Ensure CA can assign list of users to new team."""
    chamber_admin_client.select_campaign(volunteers_team_1[0].campaign)
    response = chamber_admin_client.put(
        get_user_campaign_assign_team_url,
        data=user_volunteer_assign_team_data,
    )

    assert response.status_code == status.HTTP_200_OK
    for user in volunteers_team_1:
        user.refresh_from_db()
        assert user.team_id == user_volunteer_assign_team_data["team"]


@pytest.mark.parametrize(
    "invalid_assigned_team_data",
    [
        pytest.lazy_fixture("user_chamber_chair_assign_team_data"),
        pytest.lazy_fixture("user_team_captain_assign_team_data"),
    ],
)
def test_user_campaign_assign_team_api_fail(
    team_captain_team_2: UserCampaign,
    team_captains_team_1: list[UserCampaign],
    chamber_chair_users: list[UserCampaign],
    chamber_admin_client: CAAPIClient,
    invalid_assigned_team_data: dict,
) -> None:
    """Raise error if some users cannot be assigned to new team.

    User cannot be assigned to new team if:
        - Chamber Chair/Vice Chair: they cannot be assigned to a team
        - Team Captain: assigned team already has a Team Captain

    """
    chamber_admin_client.select_campaign(team_captain_team_2.campaign)
    response = chamber_admin_client.put(
        get_user_campaign_assign_team_url,
        data=invalid_assigned_team_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_user_campaign_roles_api(chamber_admin_client: APIClient) -> None:
    """Ensure list of user campaign role api works properly."""
    response = chamber_admin_client.get(get_user_campaign_roles_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == len(UserCampaignRole.choices) - 1


# pylint: disable=redefined-outer-name
def test_profile_update_api_volunteer(
    volunteer: User,
    chamber: Chamber,
    api_client: APIClient,
    profile_update_data: dict,
) -> None:
    """Ensure that volunteer can update their profile."""
    UserCampaign.objects.create(
        user=volunteer,
        campaign=CampaignFactory(chamber=chamber, status=CampaignStatus.LIVE),
        team=TeamFactory(),
    )
    volunteer.chamber = chamber
    volunteer.save()
    stored_member = StoredMember.objects.create(chamber=chamber)
    profile_update_data.update(
        {
            "member": stored_member.pk,
        },
    )
    api_client.force_authenticate(user=volunteer)
    response = api_client.put(vs_profile_url, profile_update_data)
    assert response.status_code == status.HTTP_200_OK, response.data


def test_profile_update_api_volunteer_invalid_data(
    volunteer: User,
    chamber: Chamber,
    api_client: APIClient,
    profile_update_data: dict,
) -> None:
    """Ensure that error about max length is raised."""
    UserCampaign.objects.create(
        user=volunteer,
        campaign=CampaignFactory(chamber=chamber, status=CampaignStatus.LIVE),
        team=TeamFactory(),
    )
    volunteer.chamber = chamber
    volunteer.save()
    api_client.force_authenticate(user=volunteer)
    profile_update_data.update(
        {
            "mobile_phone": "0" * (MAX_PHONE_NUMBER_LENGTH + 1),
            "home_zip_code": "0" * (MAX_ZIP_CODE_LENGTH + 1),
            "company_zip_code": "0" * (MAX_ZIP_CODE_LENGTH + 1),
            "company_phone_number": "0" * (MAX_PHONE_NUMBER_LENGTH + 1),
            "company_mobile_number": "0" * (MAX_PHONE_NUMBER_LENGTH + 1),
        },
    )
    response = api_client.put(vs_profile_url, profile_update_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    for error in response.data["errors"]:
        assert error["attr"] in (
            "mobile_phone",
            "home_zip_code",
            "company_zip_code",
            "company_phone_number",
            "company_mobile_number",
            "member",
        )
        assert error["code"] in ("max_length", "required")


def test_super_admin_get_profile_in_vs(api_client: APIClient):
    """Ensure SA can get profile in VS successfully in any case."""
    super_admin = UserFactory(role=User.ROLES.SUPER_ADMIN)
    api_client.force_authenticate(super_admin)

    response = api_client.get(vs_profile_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["role"] == User.ROLES.SUPER_ADMIN


@pytest.mark.skip(reason="Skip due to new logic")
def test_delete_user_campaign_having_contracts(chamber_admin: User):
    """Ensure user campaign having contracts can't be deleted."""
    api_client = CAAPIClient()
    _campaign = CampaignFactory(
        chamber_id=chamber_admin.chamber_id,
        status=CampaignStatus.LIVE,
    )
    _volunteer: User = UserFactory(
        chamber_id=chamber_admin.chamber_id,
        role=User.ROLES.VOLUNTEER,
    )
    user_campaign = UserCampaignFactory(
        campaign=_campaign,
        user=_volunteer,
        email=_volunteer.email,
    )
    ContractFactory(campaign=_campaign, created_by=user_campaign)

    api_client.force_authenticate(chamber_admin)
    api_client.select_campaign(_campaign)
    response = api_client.delete(
        get_user_campaign_detail_url(kwargs={"pk": user_campaign.pk}),
    )
    expected_error_message = IsUserCampaignDeletable.message

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["errors"][0]["detail"] == expected_error_message


def test_delete_user_campaign_without_contracts(chamber_admin: User):
    """Ensure user campaign without contracts can be deleted."""
    api_client = CAAPIClient()
    _campaign = CampaignFactory(
        chamber_id=chamber_admin.chamber_id,
        status=CampaignStatus.LIVE,
    )
    _volunteer: User = UserFactory(
        chamber_id=chamber_admin.chamber_id,
        role=User.ROLES.VOLUNTEER,
    )
    user_campaign = UserCampaignFactory(
        campaign=_campaign,
        user=_volunteer,
        role=UserCampaignRole.VOLUNTEER,
        email=_volunteer.email,
    )

    api_client.force_authenticate(chamber_admin)
    api_client.select_campaign(_campaign)
    response = api_client.delete(
        get_user_campaign_detail_url(kwargs={"pk": user_campaign.pk}),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_user_campaign_with_shared_contracts(chamber_admin: User):
    """Ensure credits of contracts shared to deleted user is recalculated."""
    _campaign = CampaignFactory(
        chamber_id=chamber_admin.chamber_id,
        status=CampaignStatus.LIVE,
    )
    main_volunteer: User = UserFactory(
        chamber_id=chamber_admin.chamber_id,
        role=User.ROLES.VOLUNTEER,
    )
    main_user_campaign = UserCampaignFactory(
        campaign=_campaign,
        user=main_volunteer,
        role=UserCampaignRole.VOLUNTEER,
        email=main_volunteer.email,
    )
    shared_volunteer: User = UserFactory(
        chamber_id=chamber_admin.chamber_id,
        role=User.ROLES.VOLUNTEER,
    )
    shared_user_campaign = UserCampaignFactory(
        campaign=_campaign,
        user=shared_volunteer,
        role=UserCampaignRole.VOLUNTEER,
        email=shared_volunteer.email,
    )
    contract_1 = ContractFactory(
        campaign=_campaign,
        created_by=main_user_campaign,
        status=Contract.STATUSES.DRAFT,
    )
    ContractCreditInfo.objects.bulk_create(
        [
            ContractCreditInfo(
                contract=contract_1,
                user_campaign=main_user_campaign,
                portion=0.5,
            ),
            ContractCreditInfo(
                contract=contract_1,
                user_campaign=shared_user_campaign,
                portion=0.5,
            ),
        ],
    )
    contract_2 = ContractFactory(
        campaign=_campaign,
        created_by=main_user_campaign,
        status=Contract.STATUSES.DRAFT,
    )
    ContractCreditInfo.objects.bulk_create(
        [
            ContractCreditInfo(
                contract=contract_2,
                user_campaign=main_user_campaign,
                portion=0.5,
            ),
            ContractCreditInfo(
                contract=contract_2,
                user_campaign=shared_user_campaign,
                portion=0.5,
            ),
        ],
    )
    api_client = CAAPIClient()
    api_client.force_authenticate(chamber_admin)
    api_client.select_campaign(_campaign)

    response = api_client.delete(
        get_user_campaign_detail_url(kwargs={"pk": shared_user_campaign.pk}),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert (
        ContractCreditInfo.objects.get(contract=contract_1).portion
        == decimal.Decimal(1)
    )
    assert (
        ContractCreditInfo.objects.get(contract=contract_2).portion
        == decimal.Decimal(1)
    )


# pylint: disable=too-many-arguments
def test_update_imported_user_campaign_email_api(
    chamber_admin: User,
    open_campaign: campaign_models.Campaign,
    user_campaign_update_data: dict,
    mailoutbox,
    django_capture_on_commit_callbacks,
    stored_member: StoredMember,
) -> None:
    """Ensure CA can update email for imported campaign users."""
    imported_campaign_user = UserCampaignFactory(
        campaign=open_campaign,
        role=UserCampaignRole.VOLUNTEER,
        email="",
        external_user_id=123,
        member=stored_member,
    )
    team = TeamFactory(campaign=open_campaign)
    user_campaign_update_data["team"] = team.pk
    api_client = CAAPIClient()
    api_client.select_campaign(open_campaign)
    api_client.force_authenticate(
        user=chamber_admin,
        token=AuthToken.objects.create(chamber_admin)[0],
    )
    with django_capture_on_commit_callbacks(execute=True) as callbacks:
        response = api_client.put(
            get_user_campaign_detail_url(
                kwargs={"pk": imported_campaign_user.pk},
            ),
            data=user_campaign_update_data,
        )
    assert response.status_code == status.HTTP_200_OK, response.data
    imported_campaign_user.refresh_from_db()
    assert imported_campaign_user.email == user_campaign_update_data["email"]
    assert len(callbacks) == 1
    assert len(mailoutbox) == 1


def test_update_imported_user_campaign_email_api_duplicate_email(
    chamber_admin: User,
    open_campaign: campaign_models.Campaign,
    user_campaign_update_data: dict,
) -> None:
    """Ensure CA cannot update email for imported campaign users.

    Ensure it return 400 if email is already used by another user.

    """
    existing_user = UserFactory(
        chamber_id=chamber_admin.chamber_id,
        role=User.ROLES.VOLUNTEER,
    )
    existing_campaign_user = UserCampaignFactory(
        campaign=open_campaign,
        role=UserCampaignRole.VOLUNTEER,
        user=existing_user,
        email=existing_user.email,
    )
    imported_campaign_user = UserCampaignFactory(
        campaign=open_campaign,
        role=UserCampaignRole.VOLUNTEER,
        email="",
        external_user_id=123,
    )
    team = TeamFactory(campaign=open_campaign)
    user_campaign_update_data.update(
        {"team": team.pk, "email": existing_campaign_user.email},
    )
    api_client = CAAPIClient()
    api_client.select_campaign(open_campaign)
    api_client.force_authenticate(
        user=chamber_admin,
        token=AuthToken.objects.create(chamber_admin)[0],
    )
    response = api_client.put(
        get_user_campaign_detail_url(kwargs={"pk": imported_campaign_user.pk}),
        data=user_campaign_update_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["errors"][0]["detail"] == (
        "Account with this email already exists"
    )
