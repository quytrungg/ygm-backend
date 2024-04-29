import typing
from decimal import Decimal

from apps.campaigns import models as campaigns_models


class SaleStatisticsData(typing.TypedDict):
    """Represent structure for sale statistics data."""

    total_sold_value: Decimal
    total_available_value: Decimal
    total_sold_count: int
    total_available_count: int


def get_sale_statistics_data(campaign_id: int) -> SaleStatisticsData:
    """Return sale statistics for a campaign."""
    total_sold_value = Decimal(0)
    total_available_value = Decimal(0)
    total_sold_count = 0
    total_available_count = 0
    campaign_levels = campaigns_models.Level.objects.filter(
        product__category__campaign_id=campaign_id,
    ).with_sale_report_data()

    for level in campaign_levels:
        total_sold_value += level.sold_value
        total_sold_count += level.sold_instances_count
        if level.amount < 0:
            continue
        total_available_value += level.remaining_value
        total_available_count += (
            level.total_instances_count - level.sold_instances_count
        )

    return SaleStatisticsData(
        total_sold_value=total_sold_value,
        total_available_value=total_available_value,
        total_sold_count=total_sold_count,
        total_available_count=total_available_count,
    )
