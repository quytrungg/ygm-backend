# Generated by Django 4.2.2 on 2023-09-13 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0007_contract_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='signed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Signed at'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('pending_approval', 'Pending Approval'), ('approved', 'Approved'), ('sent', 'Sent'), ('declined', 'Declined'), ('signed', 'Signed')], default='draft', max_length=20, verbose_name='Status'),
        ),
    ]
