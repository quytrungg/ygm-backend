# Generated by Django 4.2.7 on 2023-11-23 07:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0036_auto_20231116_1107'),
        ('members', '0014_alter_contract_name'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ContractSharedCreditInfo',
            new_name='ContractCreditInfo',
        ),
    ]