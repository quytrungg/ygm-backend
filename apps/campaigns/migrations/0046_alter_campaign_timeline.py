# Generated by Django 4.2.9 on 2024-02-02 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0045_level_external_id_level_external_multiplier_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='timeline',
            field=models.CharField(choices=[('23os_tc', '23OS TC'), ('23os_vc', '23OS VC')], max_length=255, verbose_name='Timeline Applied'),
        ),
    ]
