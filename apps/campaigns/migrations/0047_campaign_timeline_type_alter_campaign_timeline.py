# Generated by Django 4.2.9 on 2024-02-02 08:24

from django.db import migrations, models
import django.db.models.deletion


def populate_current_campaigns(apps, schema_editor):
    """Populate campaigns with `timeline_type` and `timeline` fields."""
    Campaign = apps.get_model("campaigns", "Campaign")
    TimelineType = apps.get_model("timelines", "TimelineType")
    campaigns = Campaign.objects.all()
    for campaign in campaigns:
        campaign.timeline = TimelineType.objects.filter(
            name=campaign.timeline_type,
        ).first()
    Campaign.objects.bulk_update(campaigns, ["timeline"])


def reverse_populate_current_campaigns(apps, schema_editor):
    """Reverse current campaigns with `timeline` and `timeline_type` fields."""
    Campaign = apps.get_model("campaigns", "Campaign")
    campaigns = Campaign.objects.all()
    for campaign in campaigns:
        campaign.timeline_type = (
            campaign.timeline.name if campaign.timeline else ""
        )
    Campaign.objects.bulk_update(campaigns, ["timeline_type"])


class Migration(migrations.Migration):

    dependencies = [
        ('timelines', '0011_timelinetype_rename_type_timeline_type_name'),
        ('campaigns', '0046_alter_campaign_timeline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='timeline',
            field=models.CharField(blank=True, choices=[('23os_tc', '23OS TC'), ('23os_vc', '23OS VC')], max_length=255, verbose_name='Timeline Type'),
        ),
        migrations.RenameField(
            model_name='campaign',
            old_name='timeline',
            new_name='timeline_type',
        ),
        migrations.AddField(
            model_name='campaign',
            name='timeline',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='campaigns', to='timelines.timelinetype', verbose_name='Timeline Applied'),
        ),
        migrations.RunPython(
            populate_current_campaigns,
            reverse_code=reverse_populate_current_campaigns,
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='timeline_type',
        ),
    ]
