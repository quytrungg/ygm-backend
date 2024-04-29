from django.db import migrations, models
from datetime import date


def modify_campaign_date(apps, schema_editor):
    """Set campaign start date."""
    Campaign = apps.get_model("campaigns", "Campaign")
    updated_campaigns = [
        campaign
        for campaign in Campaign.objects.filter(start_date__isnull=False)
        if campaign.start_date == date(campaign.year, 12, 31)
    ]
    for campaign in updated_campaigns:
        if campaign.status not in ("live", "done"):
            campaign.start_date = None
            continue
        campaign.start_date = date(campaign.year, 1, 1)
    Campaign.objects.bulk_update(updated_campaigns, ["start_date"])


class Migration(migrations.Migration):
    dependencies = [
        ("campaigns", "0034_usercampaign_sales_goal"),
    ]

    operations = [
        migrations.RunPython(
            code=modify_campaign_date,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
