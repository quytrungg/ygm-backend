# Generated by Django 4.2.5 on 2023-10-10 02:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('campaigns', '0022_levelinstance_trade_with'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('deleted_at', models.DateTimeField(db_index=True, editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('type', models.CharField(choices=[('contract_note', 'Contract Note'), ('invoice_note', 'Invoice Note'), ('thankyou_letter', 'Thank You Letter'), ('pe_thankyou_letter', 'Post Event Thank You Letter'), ('company_thankyou_letter', 'Company Thank You Letter'), ('reward_email', 'Reward Email'), ('renewal_letter', 'Renewal Letter'), ('renewal_contract', 'Renewal Contract')], max_length=255, verbose_name='Note Type')),
                ('body', models.TextField(verbose_name='Note text')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='campaigns.campaign', verbose_name='Campaign ID')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]