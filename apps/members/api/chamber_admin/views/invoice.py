from decimal import Decimal

from django.db.models import Count, F, Q, Sum, functions
from django.utils import timezone

from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from apps.core.api.permissions import AllowChamberAdmin, IsCampaignInProgress
from apps.core.api.views import ChamberBaseViewSet
from apps.members.models import Invoice
from apps.members.tasks import send_invoice_email

from .. import serializers


class InvoiceViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    ChamberBaseViewSet,
):
    """Invoice management for chamber admin and super admin."""

    queryset = Invoice.objects.all()
    serializer_class = serializers.InvoiceDetailSerializer
    serializers_map = {
        "list": serializers.ListInvoiceSerializer,
        "retrieve": serializers.InvoiceDetailSerializer,
        "default": serializers.InvoiceDetailSerializer,
    }
    permissions_map = {
        "default": (AllowChamberAdmin, IsCampaignInProgress),
        "list": (AllowChamberAdmin,),
        "retrieve": (AllowChamberAdmin,),
    }
    ordering_fields = ("contract_name",)
    search_fields = ()

    def get_queryset(self):
        """Return list of invoices within current campaign."""
        qs = super().get_queryset().annotate(
            contract_name=F("contract__name"),
        )
        campaign = getattr(self.request, "campaign", None)
        if not campaign:
            return qs.none()

        qs = qs.filter(contract__campaign_id=campaign.id)
        if self.action == "retrieve":
            return qs.select_related("contract").prefetch_related(
                "contract__levels__level__product",
                "contract__campaign__chamber",
            )
        return qs.annotate(
            levels_count=Count(
                "contract__levels",
                filter=Q(
                    contract__levels__deleted_at__isnull=True,
                    contract__levels__declined_at__isnull=True,
                ),
            ),
            cost=functions.Coalesce(
                Sum(
                    "contract__levels__cost",
                    filter=Q(
                        contract__levels__deleted_at__isnull=True,
                        contract__levels__declined_at__isnull=True,
                    ),
                ),
                Decimal(0),
            ),
        ).order_by("contract_name")

    @extend_schema(request=None)
    @action(detail=True, methods=("post",), url_name="pay", url_path="pay")
    def mark_invoice_paid(self, *args, **kwargs) -> Response:
        """Mark selected invoice as paid."""
        invoice = self.get_object()
        invoice.mark_paid()
        return Response()

    @extend_schema(request=None)
    @action(detail=True, methods=("post",), url_path="send-invoice")
    def send_invoice(self, *args, **kwargs) -> Response:
        """Send invoice email to member."""
        invoice = self.get_object()
        invoice.sent_at = timezone.now()
        invoice.save()
        send_invoice_email.delay(invoice_id=invoice.pk)
        return Response()
