# Generated by Django 4.2.2 on 2023-07-25 07:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ('campaigns', '0010_levelinstance_declined_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Start Date'),
        ),
    ]