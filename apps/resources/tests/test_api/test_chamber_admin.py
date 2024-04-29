from django.urls import reverse_lazy

from rest_framework import status, test

from apps.chambers.models.chamber import Chamber
from apps.users.models.user import User


def test_resource_category_create(
    api_client: test.APIClient,
    chamber_admin: User,
    chamber: Chamber,
) -> None:
    """Ensure parent-category could be created."""
    chamber_admin.chamber = chamber
    chamber_admin.save()
    api_client.force_authenticate(chamber_admin)
    url = reverse_lazy("v1:chamber:resource-category-list")
    response = api_client.post(
        url,
        data={
            "name": "Parent Cat",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
