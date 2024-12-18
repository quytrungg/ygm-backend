# Generated by Django 4.2.2 on 2023-06-14 02:52

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Is paid')),
            ],
            options={
                'verbose_name': 'Invoice',
                'verbose_name_plural': 'Invoices',
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('address', models.CharField(max_length=255, verbose_name='Address')),
                ('city', models.CharField(max_length=255, verbose_name='City')),
                ('state', models.CharField(max_length=2, verbose_name='State')),
                ('zip_code', models.CharField(max_length=5, verbose_name='Zip code')),
                ('country', models.CharField(max_length=255, verbose_name='Country')),
                ('phone', models.CharField(max_length=15, verbose_name='Phone number')),
                ('fax', models.CharField(max_length=15, verbose_name='Fax number')),
                ('contact_methods', models.CharField(max_length=255, verbose_name='Contact methods')),
            ],
            options={
                'verbose_name': 'Member',
                'verbose_name_plural': 'Members',
            },
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('status', models.CharField(max_length=20, verbose_name='Status')),
                ('is_approved', models.BooleanField(default=False, verbose_name='Approved')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='members.invoice', verbose_name='Invoice')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='members.member', verbose_name='Member')),
            ],
            options={
                'verbose_name': 'Contract',
                'verbose_name_plural': 'Contracts',
            },
        ),
    ]
