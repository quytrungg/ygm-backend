from apps.campaigns.models import ProductAttachment
from apps.core.api.serializers import (
    BaseReorderSerializer,
    ModelBaseSerializer,
)


class ProductAttachmentReorderSerializer(
    ModelBaseSerializer,
    BaseReorderSerializer,
):
    """Represent ProductAttachment's order information."""

    class Meta(BaseReorderSerializer.Meta):
        model = ProductAttachment
