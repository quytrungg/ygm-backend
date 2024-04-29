from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.api.permissions import AllowChamberAdmin, IsCampaignInProgress
from apps.core.api.views import ChamberBaseViewSet

from ....models import ProductAttachment
from ..serializers import ProductAttachmentReorderSerializer


class ProductAttachmentViewSet(ChamberBaseViewSet):
    """Viewset for chamber admin to manage ProductAttachment."""

    queryset = ProductAttachment.objects.all().order_by("order")
    serializer_class = ProductAttachmentReorderSerializer
    permission_classes = (AllowChamberAdmin, IsCampaignInProgress)
    search_fields = ()
    ordering_fields = ()

    @action(detail=True, methods=("put",))
    def reorder(self, request, *args, **kwargs) -> Response:
        """Reorder items in product attachment lists."""
        product_attachment = self.get_object()
        serializer = self.get_serializer(product_attachment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
