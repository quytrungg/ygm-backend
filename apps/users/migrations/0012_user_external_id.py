# Generated by Django 4.2.7 on 2023-12-22 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_alter_user_email_user_unique_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='external_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID in old DB'),
        ),
        migrations.AddField(
            model_name='user',
            name='external_chamber_id',
            field=models.IntegerField(
                blank=True, null=True,
                verbose_name='chamber ID in old DB',
            ),
        ),
    ]