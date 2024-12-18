# Generated by Django 4.2.10 on 2024-04-03 06:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0023_contract_signer_ip_address"),
    ]

    operations = [
        migrations.AlterField(
            model_name="member",
            name="mobile_phone",
            field=models.CharField(
                blank=True, max_length=20, verbose_name="Mobile Phone number",
            ),
        ),
        migrations.AlterField(
            model_name="member",
            name="work_phone",
            field=models.CharField(
                blank=True, max_length=20, verbose_name="Work Phone number",
            ),
        ),
    ]
