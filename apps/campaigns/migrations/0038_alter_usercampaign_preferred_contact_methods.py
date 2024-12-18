# Generated by Django 4.2.7 on 2023-12-04 03:09

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0037_alter_campaign_report_close_on_end_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercampaign',
            name='preferred_contact_methods',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=255), default=list, size=None, verbose_name='Preferred contact methods'),
        ),
    ]
