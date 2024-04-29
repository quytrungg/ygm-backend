# Generated by Django 4.2.2 on 2023-07-27 03:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('campaigns', '0011_alter_campaign_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='productcategory',
            name='background_color',
            field=models.CharField(blank=True, max_length=6, verbose_name='Background Color'),
        ),
        migrations.AlterField(
            model_name='productcategory',
            name='image',
            field=models.ImageField(blank=True, max_length=1000, null=True, upload_to='', verbose_name='Image'),
        ),
    ]
