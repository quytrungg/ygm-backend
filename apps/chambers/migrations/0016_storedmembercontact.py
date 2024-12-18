# Generated by Django 4.2.7 on 2024-01-12 02:05

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('chambers', '0015_alter_storedmember_options_alter_chamber_subdomain'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoredMemberContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('deleted_at', models.DateTimeField(db_index=True, editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('first_name', models.CharField(blank=True, max_length=255, verbose_name='Contact First Name')),
                ('last_name', models.CharField(blank=True, max_length=255, verbose_name='Last Name')),
                ('email', models.EmailField(max_length=255, verbose_name='Email')),
                ('work_phone', models.CharField(blank=True, max_length=20, verbose_name='Work Phone')),
                ('mobile_phone', models.CharField(blank=True, max_length=20, verbose_name='Mobile Phone')),
                ('stored_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='chambers.storedmember', verbose_name='Stored Member')),
            ],
            options={
                'verbose_name': 'Stored Member Contact',
                'verbose_name_plural': 'Stored Member Contacts',
            },
        ),
    ]
