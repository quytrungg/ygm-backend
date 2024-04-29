from django.urls import reverse_lazy

from rest_framework import status, test

from apps.users.models.user import User


def test_resource_category_create(
    api_client: test.APIClient,
    super_admin: User,
) -> None:
    """Ensure parent-category could be created."""
    api_client.force_authenticate(super_admin)
    url = reverse_lazy("v1:super-admin:resource-category-list")
    response = api_client.post(
        url,
        data={
            "name": "Parent Cat",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
