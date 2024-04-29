# Generated by Django 4.2.2 on 2023-07-18 07:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('campaigns', '0008_alter_usercampaign_role'),
        ('members', '0002_contract_deleted_at_contract_deleted_by_cascade_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='campaign',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='campaigns.campaign', verbose_name='Campaign ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contract',
            name='name',
            field=models.CharField(default=1, max_length=255, verbose_name='Name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contract',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('pending_approval', 'Pending Approval'), ('approved', 'Approved'), ('sent', 'Sent'), ('declined', 'Declined')], default='draft', max_length=20, verbose_name='Status'),
        ),
    ]