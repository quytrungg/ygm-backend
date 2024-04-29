from config.celery import app

from apps.members.notifications import InvoiceEmailNotification

from .models import Invoice


@app.task
def send_invoice_email(invoice_id: int) -> None:
    """Send welcome email to new chamber admin."""
    invoice = Invoice.objects.filter(pk=invoice_id).first()
    if not invoice:
        return
    InvoiceEmailNotification(invoice=invoice).send()
