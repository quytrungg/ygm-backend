# Generated by Django 4.2.5 on 2023-11-23 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0013_remove_invoice_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='name',
            field=models.CharField(editable=False, max_length=255, verbose_name='Name'),
        ),
    ]