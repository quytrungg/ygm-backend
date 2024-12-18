# Generated by Django 4.2.5 on 2023-11-02 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0030_rename_company_fax_number_usercampaign_company_mobile_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productattachment',
            name='external_url',
            field=models.URLField(blank=True, max_length=255, verbose_name='External URL'),
        ),
        migrations.AlterField(
            model_name='productattachment',
            name='file',
            field=models.FileField(blank=True, max_length=1000, null=True, upload_to='', verbose_name='Media File'),
        ),
    ]
