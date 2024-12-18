# Generated by Django 4.2.2 on 2023-08-09 03:01

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):
    dependencies = [
        ('chambers', '0009_alter_chamber_nickname_alter_chamber_subdomain_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoredMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('deleted_at', models.DateTimeField(db_index=True, editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('first_name', models.CharField(blank=True, max_length=255, verbose_name='First Name')),
                ('last_name', models.CharField(blank=True, max_length=255, verbose_name='Last Name')),
                ('email', models.EmailField(blank=True, max_length=255, verbose_name='Email')),
                ('phone', models.CharField(blank=True, max_length=15, verbose_name='Phone')),
                ('external_id', models.CharField(blank=True, max_length=255, verbose_name='External Id')),
                ('chamber', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chambers.chamber', verbose_name='Chamber')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
