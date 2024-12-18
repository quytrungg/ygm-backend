# Generated by Django 4.2.2 on 2023-08-30 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0015_alter_usercampaign_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usercampaign',
            name='company_country',
        ),
        migrations.AlterField(
            model_name='usercampaign',
            name='company_fax_number',
            field=models.CharField(blank=True, max_length=20, verbose_name='Company fax number'),
        ),
        migrations.AlterField(
            model_name='usercampaign',
            name='company_phone_number',
            field=models.CharField(blank=True, max_length=20, verbose_name='Company phone number'),
        ),
        migrations.AlterField(
            model_name='usercampaign',
            name='company_zip_code',
            field=models.CharField(blank=True, max_length=15, verbose_name='Company zip code'),
        ),
    ]
