# Generated by Django 4.2.5 on 2023-11-08 10:30

from django.db import migrations, models
from datetime import date

def set_campaign_end_date(apps, schema_editor):
    """Set campaign end date."""
    Campaign = apps.get_model("campaigns", "Campaign")
    updated_campaigns = list(Campaign.objects.all())
    for campaign in updated_campaigns:
        campaign.end_date = date(campaign.year, 12, 31)
    Campaign.objects.bulk_update(updated_campaigns, ["end_date"])

class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0031_productattachment_external_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='end_date',
            field=models.DateField(blank=True, null=True, verbose_name='End Date'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='start_date',
            field=models.DateField(blank=True, null=True, verbose_name='Start Date to be Active'),
        ),
        migrations.RunPython(
            code=set_campaign_end_date,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
