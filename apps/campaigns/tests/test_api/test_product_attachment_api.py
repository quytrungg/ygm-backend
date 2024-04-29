from django.urls import reverse_lazy

from rest_framework import status

from apps.campaigns.factories import (
    ProductAttachmentFactory,
    ProductCategoryFactory,
    ProductFactory,
)
from apps.campaigns.models import Campaign, ProductAttachment
from apps.core.test_utils import CAAPIClient


def test_product_attachment_reorder_api(
    chamber_admin_client: CAAPIClient,
    campaign: Campaign,
) -> None:
    """Ensure chamber admin to reorder product attachment to new index."""
    category = ProductCategoryFactory(campaign=campaign)
    product = ProductFactory(category=category)
    ProductAttachmentFactory.create_batch(10, product=product)
    attachments = list(ProductAttachment.objects.filter(product=product))
    attachment = attachments[0]
    orders = list(range(len(attachments)))
    chamber_admin_client.select_campaign(campaign)
    response = chamber_admin_client.put(
        reverse_lazy(
            "v1:chamber:product-attachment-reorder",
            kwargs={"pk": attachment.id},
        ),
        data={"order": len(attachments) - 1},
    )
    assert response.status_code == status.HTTP_200_OK
    for attachment in attachments:
        attachment.refresh_from_db()
    assert [
        attachment.order
        for attachment in attachments
    ] == orders[-1:] + orders[:-1]
