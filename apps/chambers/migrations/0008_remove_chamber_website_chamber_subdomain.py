# Generated by Django 4.2.2 on 2023-07-21 04:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('chambers', '0007_alter_chamber_nickname'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chamber',
            name='website',
        ),
        migrations.AddField(
            model_name='chamber',
            name='subdomain',
            field=models.CharField(max_length=63, null=True, unique=True, verbose_name='Subdomain'),
        ),
    ]
