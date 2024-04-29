from django.db import migrations, models
from datetime import date


def set_campaign_start_date(apps, schema_editor):
    """Set campaign start date."""
    Campaign = apps.get_model("campaigns", "Campaign")
    updated_campaigns = list(Campaign.objects.filter(start_date__isnull=True))
    for campaign in updated_campaigns:
        campaign.start_date = date(campaign.year, 12, 31)
    Campaign.objects.bulk_update(updated_campaigns, ["start_date"])


class Migration(migrations.Migration):
    dependencies = [
        ("campaigns", "0032_campaign_end_date_campaign_start_date"),
    ]

    operations = [
        migrations.RunPython(
            code=set_campaign_start_date,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
