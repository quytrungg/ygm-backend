from functools import partial

from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.test import APIClient

import pytest

from apps.chambers.models import Chamber, StoredMember, StoredMemberContact
from apps.users.constants import UserRole
from apps.users.factories import UserFactory


def get_stored_member_url(action_name: str, kwargs=None):
    """Return url for super admin chamber api."""
    return reverse_lazy(
        f"v1:chamber:stored-member-{action_name}",
        kwargs=kwargs,
    )


list_stored_member_url = get_stored_member_url(action_name="list")
detail_chamber_url = partial(get_stored_member_url, action_name="detail")


@pytest.fixture
def stored_member_creation_data():
    """Return a factory for StoredMember creation data."""
    def _build(**kwargs):
        """Return data for StoredMember creation."""
        default = {
            "name": "ABC",
            "address": "DEF",
            "city": "",
            "state": "",
            "zip": "",
            "contacts": [],
        }
        default.update(kwargs)
        return default
    return _build


def test_create_stored_member(
    chamber: Chamber,
    api_client: APIClient,
    stored_member_creation_data,
):
    """Ensure `StoredMember` can be created with valid data."""
    chamber_admin = UserFactory(role=UserRole.CHAMBER_ADMIN, chamber=chamber)
    api_client.force_authenticate(chamber_admin)
    contacts_info = [
        {
            "first_name": "Contact",
            "last_name": "C1",
            "email": "c1@mail.com",
            "work_phone": "1981234567",
            "mobile_phone": "1981234567",
        },
    ]
    creation_data = stored_member_creation_data(
        contacts=contacts_info,
        name="Success",
    )
    response = api_client.post(
        list_stored_member_url,
        data=creation_data,
    )

    new_member = StoredMember.objects.filter(
        chamber=chamber,
        name=creation_data["name"],
    ).first()

    assert response.status_code == status.HTTP_201_CREATED
    assert new_member is not None
    assert StoredMemberContact.objects.filter(
        stored_member=new_member,
        email=contacts_info[0]["email"],
    ).count() == 1


def test_cannot_create_stored_member_with_duplicate_contact_emails(
    chamber: Chamber,
    api_client: APIClient,
    stored_member_creation_data,
):
    """Ensure creation fails if there are duplicated contact emails."""
    chamber_admin = UserFactory(role=UserRole.CHAMBER_ADMIN, chamber=chamber)
    api_client.force_authenticate(chamber_admin)
    contacts_info = [
        {
            "first_name": "Contact",
            "last_name": "C1",
            "email": "duplicate@mail.com",
            "work_phone": "1981234567",
            "mobile_phone": "1981234567",
        },
        {
            "first_name": "Contact",
            "last_name": "C2",
            "email": "contact@mail.com",
            "work_phone": "1981234567",
            "mobile_phone": "1981234567",
        },
        {
            "first_name": "Contact",
            "last_name": "C3",
            "email": "duplicate@mail.com",
            "work_phone": "1981234567",
            "mobile_phone": "1981234567",
        },
    ]
    creation_data = stored_member_creation_data(
        contacts=contacts_info,
        name="Fail",
    )
    response = api_client.post(
        list_stored_member_url,
        data=creation_data,
    )

    new_member = StoredMember.objects.filter(
        chamber=chamber,
        name=creation_data["name"],
    ).first()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert new_member is None
    error_attrs = [
        error["attr"] for error in response.data["errors"]
    ]
    assert error_attrs == ["contacts.0.email", "contacts.2.email"]
