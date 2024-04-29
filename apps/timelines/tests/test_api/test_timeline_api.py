from functools import partial

from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.test import APIClient

import pytest

from apps.campaigns.factories import CampaignFactory
from apps.campaigns.models import Campaign
from apps.chambers.models import Chamber
from apps.core.test_utils import CAAPIClient
from apps.users.factories import UserFactory
from apps.users.models import User

from ...constants import (
    TimelineCategoryNames,
    TimelineStatus,
    TimelineTypeChoice,
)
from ...factories import TimelineFactory
from ...models import Timeline, TimelineType


def get_timeline_url(namespace: str, action_name: str, kwargs=None) -> str:
    """Return appropriate timeline url with given namespace and action name."""
    return reverse_lazy(
        f"v1:{namespace}:timeline-{action_name}",
        kwargs=kwargs,
    )


list_timeline_url = get_timeline_url("chamber", "list")
detail_timeline_url = partial(
    get_timeline_url,
    namespace="chamber",
    action_name="detail",
)
reorder_timeline_url = partial(
    get_timeline_url,
    namespace="chamber",
    action_name="reorder",
)


@pytest.fixture
def open_campaign(chamber_admin: User) -> Campaign:
    """Return open campaign for chamber admin."""
    return CampaignFactory(
        status=Campaign.STATUSES.CREATED,
        chamber=chamber_admin.chamber,
        timeline_id=TimelineType.objects.get(
            name=TimelineTypeChoice.WITHOUT_VICE_CHAIR,
        ).id,
    )


def test_timeline_list_api(chamber_admin_client: APIClient) -> None:
    """Ensure SA and CA can access timeline list api."""
    response = chamber_admin_client.get(list_timeline_url)
    assert response.status_code == status.HTTP_200_OK


def test_timeline_list_api_fail(api_client: APIClient) -> None:
    """Ensure non-admin users cannot access admin timeline list api."""
    normal_user = UserFactory()
    api_client.force_authenticate(normal_user)
    response = api_client.get(list_timeline_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_timeline_detail_api(
    chamber_admin_client: APIClient,
    timeline: Timeline,
) -> None:
    """Ensure SA and CA can access timeline detail api."""
    response = chamber_admin_client.get(
        detail_timeline_url(kwargs={"pk": timeline.pk}),
    )
    assert response.status_code == status.HTTP_200_OK


def test_timeline_detail_api_fail(
    chamber_admin_client: APIClient,
    another_timeline: Timeline,
) -> None:
    """Ensure CA cannot access to timelines from other chambers."""
    response = chamber_admin_client.get(
        detail_timeline_url(kwargs={"pk": another_timeline.pk}),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_timeline_create_api(
    chamber_admin: User,
    open_campaign: Campaign,
    timeline_create_data: dict,
) -> None:
    """Ensure CA can create a new timeline."""
    api_client = CAAPIClient()
    api_client.select_campaign(open_campaign)
    api_client.force_authenticate(chamber_admin)
    response = api_client.post(list_timeline_url, data=timeline_create_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Timeline.objects.filter(name=timeline_create_data["name"]).exists()


def test_timeline_create_api_with_type(
    chamber_admin: User,
    open_campaign: Campaign,
    timeline_create_data: dict,
) -> None:
    """Ensure CA can create new timeline with type from campaign's timeline."""
    api_client = CAAPIClient()
    api_client.select_campaign(open_campaign)
    api_client.force_authenticate(chamber_admin)
    response = api_client.post(list_timeline_url, data=timeline_create_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Timeline.objects.filter(
        name=timeline_create_data["name"],
        type_id=open_campaign.timeline_id,
    ).exists()


def test_timeline_update_api(
    chamber_admin: User,
    open_campaign: Campaign,
    timeline: Timeline,
    timeline_create_data: dict,
) -> None:
    """Ensure CA can update a timeline."""
    timeline.type_id = open_campaign.timeline_id
    timeline.save()
    api_client = CAAPIClient()
    api_client.select_campaign(open_campaign)
    api_client.force_authenticate(chamber_admin)
    response = api_client.put(
        path=detail_timeline_url(kwargs={"pk": timeline.pk}),
        data=timeline_create_data,
    )
    timeline.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert Timeline.objects.filter(
        pk=timeline.pk,
        name=timeline_create_data["name"],
    ).exists()


def test_completed_timeline_update_api(
    chamber_admin: User,
    api_client: APIClient,
    timeline_create_data: dict,
) -> None:
    """Ensure CA cannot update a completed timeline."""
    timeline = TimelineFactory(
        chamber_id=chamber_admin.chamber_id,
        status=TimelineStatus.COMPLETED,
    )
    api_client.force_authenticate(chamber_admin)
    response = api_client.put(
        path=detail_timeline_url(kwargs={"pk": timeline.pk}),
        data=timeline_create_data,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_timeline_category_list_api(
    chamber_admin_client: APIClient,
) -> None:
    """Ensure timeline category list API works properly."""
    response = chamber_admin_client.get(
        reverse_lazy("v1:chamber:timeline-category-list"),
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == len(TimelineCategoryNames)


def test_timeline_reorder_api(
    chamber_admin_client: APIClient,
    chamber: Chamber,
) -> None:
    """Ensure CA can reorder timeline to new index."""
    timelines = TimelineFactory.create_batch(
        size=5,
        chamber=chamber,
        type=TimelineType.objects.get(name=TimelineTypeChoice.WITH_VICE_CHAIR),
    )
    timeline = timelines[0]
    orders = list(range(len(timelines)))
    assert [timeline.order for timeline in timelines] == orders
    response = chamber_admin_client.put(
        reorder_timeline_url(kwargs={"pk": timeline.pk}),
        data={"order": len(timelines) - 1},
    )
    assert response.status_code == status.HTTP_200_OK
    for timeline in timelines:
        timeline.refresh_from_db()
    assert [timeline.order for timeline in timelines] == (
        orders[-1:] + orders[:-1]
    )


def test_timeline_reorder_api_fail(
    chamber_admin_client: APIClient,
    chamber: Chamber,
) -> None:
    """Ensure timelines cannot be updated with too large index/order."""
    timelines = TimelineFactory.create_batch(size=5, chamber=chamber)
    timeline = timelines[0]
    response = chamber_admin_client.put(
        reorder_timeline_url(kwargs={"pk": timeline.pk}),
        data={"order": len(timelines)},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_timeline_delete_api(
    chamber_admin_client: APIClient,
    chamber: Chamber,
) -> None:
    """Ensure CA can delete timeline and their indexes or reorganized."""
    timelines = TimelineFactory.create_batch(
        size=5,
        chamber=chamber,
        type=TimelineType.objects.get(name=TimelineTypeChoice.WITH_VICE_CHAIR),
    )
    timeline = timelines[int(len(timelines) / 2)]
    assert max(timeline.order for timeline in timelines) == len(timelines) - 1
    response = chamber_admin_client.delete(
        detail_timeline_url(kwargs={"pk": timeline.pk}),
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    for timeline in timelines:
        timeline.refresh_from_db()
    assert max(timeline.order for timeline in timelines) == len(timelines) - 2
