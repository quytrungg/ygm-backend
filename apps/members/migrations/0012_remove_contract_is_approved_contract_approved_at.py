# Generated by Django 4.2.5 on 2023-11-01 04:06

from django.db import migrations, models


def populate_contract_approved_at_field(apps, schema_editor) -> None:
    """Populate approved contracts with `approved_at` field."""
    Contract = apps.get_model("members", "Contract")
    Contract.objects.filter(status="approved").update(
        approved_at=models.F("modified"),
    )


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0011_contract_signature'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contract',
            name='is_approved',
        ),
        migrations.AddField(
            model_name='contract',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Approved At'),
        ),
        migrations.RunPython(
            populate_contract_approved_at_field,
            reverse_code=migrations.RunPython.noop,
        ),
    ]