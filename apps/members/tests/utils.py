from decimal import Decimal

from apps.members.models import Invoice


def calculate_invoice_cost_and_level_count(invoice_id: int) -> dict:
    """Calculate the expected cost and level count of an invoice."""
    invoice = Invoice.objects.filter(id=invoice_id).select_related(
        "contract",
    ).first()
    cost = Decimal(0)
    levels_count = 0
    for level in invoice.contract.levels.all():
        if level.declined_at:
            continue
        levels_count += 1
        cost += level.cost
    return {
        "cost": cost,
        "levels_count": levels_count,
    }
