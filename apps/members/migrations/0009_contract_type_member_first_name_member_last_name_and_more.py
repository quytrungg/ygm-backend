# Generated by Django 4.2.5 on 2023-10-03 10:50

from django.db import migrations, models


def update_contract_status(apps, schema_editor) -> None:
    """Change `pending_approval` status to `sent`."""
    Contract = apps.get_model("members.Contract")
    Contract.objects.filter(status="pending_approval").update(status="sent")


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0008_contract_signed_at_alter_contract_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='type',
            field=models.CharField(choices=[('cash', 'Cash'), ('trade', 'Trade')], default='cash', max_length=20, verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='member',
            name='first_name',
            field=models.CharField(default='', max_length=255, verbose_name='First name'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='member',
            name='last_name',
            field=models.CharField(default='', max_length=255, verbose_name='Last name'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='member',
            name='mobile_phone',
            field=models.CharField(default='', max_length=15, verbose_name='Mobile Phone number'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='member',
            name='work_phone',
            field=models.CharField(default='', max_length=15, verbose_name='Work Phone number'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contract',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('approved', 'Approved'), ('sent', 'Sent'), ('declined', 'Declined'), ('signed', 'Signed')], default='draft', max_length=20, verbose_name='Status'),
        ),
    ]
