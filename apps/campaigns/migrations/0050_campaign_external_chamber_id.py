# Generated by Django 4.2.9 on 2024-02-26 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0049_remove_campaign_report_close_on_end_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='external_chamber_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Chamber ID in old DB'),
        ),
    ]
