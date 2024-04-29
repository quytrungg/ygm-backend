# Generated by Django 4.2.2 on 2023-07-06 07:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('campaigns', '0004_rename_productmedia_productattachment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productattachment',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='campaigns.product', verbose_name='Product ID'),
        ),
    ]
