# Generated by Django 4.2.9 on 2024-02-27 02:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0021_contract_external_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='mobile_phone',
            field=models.CharField(max_length=20, verbose_name='Mobile Phone number'),
        ),
        migrations.AlterField(
            model_name='member',
            name='phone',
            field=models.CharField(max_length=20, verbose_name='Phone number'),
        ),
        migrations.AlterField(
            model_name='member',
            name='work_phone',
            field=models.CharField(max_length=20, verbose_name='Work Phone number'),
        ),
    ]