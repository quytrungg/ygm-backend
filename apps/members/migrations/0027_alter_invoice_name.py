# Generated by Django 4.2.10 on 2024-04-15 10:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0026_alter_contract_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="name",
            field=models.CharField(max_length=300, verbose_name="Name"),
        ),
    ]