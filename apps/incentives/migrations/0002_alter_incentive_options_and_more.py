# Generated by Django 4.2.2 on 2023-07-13 04:32

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('incentives', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='incentive',
            options={'verbose_name': 'Incentive', 'verbose_name_plural': 'Incentives'},
        ),
        migrations.AlterModelOptions(
            name='incentivequalifier',
            options={'verbose_name': 'Incentive Qualifier', 'verbose_name_plural': 'Incentive Qualifiers'},
        ),
    ]