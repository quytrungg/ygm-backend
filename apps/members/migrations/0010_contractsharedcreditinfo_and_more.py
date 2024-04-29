# Generated by Django 4.2.5 on 2023-10-06 03:46

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0022_levelinstance_trade_with'),
        ('members', '0009_contract_type_member_first_name_member_last_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractSharedCreditInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shared_credits_info', to='members.contract', verbose_name='Contract')),
                ('user_campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shared_credits_info', to='campaigns.usercampaign', verbose_name='User campaign')),
            ],
            options={
                'verbose_name': 'Contract Shared Credit Info',
                'verbose_name_plural': 'Contract Shared Credits Info',
            },
        ),
        migrations.AddField(
            model_name='contract',
            name='shared_credits_with',
            field=models.ManyToManyField(blank=True, related_name='shared_contracts', through='members.ContractSharedCreditInfo', to='campaigns.usercampaign', verbose_name='Shared credits with'),
        ),
    ]