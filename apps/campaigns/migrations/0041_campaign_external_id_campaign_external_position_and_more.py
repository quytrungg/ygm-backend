# Generated by Django 4.2.9 on 2024-01-16 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0040_level_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='external_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID in old DB'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='external_position',
            field=models.IntegerField(blank=True, null=True, verbose_name='Position in Old DB'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='external_type',
            field=models.CharField(blank=True, max_length=50, verbose_name='Type In Old DB'),
        ),
    ]
