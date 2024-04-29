from typing import TYPE_CHECKING

from django.urls import reverse_lazy

from rest_framework import status

from apps.core.test_utils import CAAPIClient

if TYPE_CHECKING:
    from apps.campaigns.models import Campaign
    from apps.users.models import User


def test_note_update_invalid(
    chamber_admin: "User",
    active_campaign: "Campaign",
):
    """Ensure that non-valid template is not allowed in note."""
    chamber_admin.chamber = active_campaign.chamber
    chamber_admin.save()
    note = active_campaign.notes.first()
    api_client = CAAPIClient()
    api_client.select_campaign(active_campaign)
    api_client.force_authenticate(chamber_admin)
    url = reverse_lazy(
        "v1:chamber:note-detail",
        kwargs={"pk": note.id},
    )
    response = api_client.put(
        url,
        data={
            "body": "Invalid syntax like: {{\"DATE}}",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
