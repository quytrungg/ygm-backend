# Generated by Django 4.2.7 on 2023-12-22 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chambers', '0015_alter_storedmember_options_alter_chamber_subdomain'),
    ]

    operations = [
        migrations.AddField(
            model_name='chamber',
            name='external_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID from old db'),
        ),
    ]
