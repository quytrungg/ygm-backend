# Generated by Django 4.2.9 on 2024-02-20 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chambers', '0018_storedmember_address2_storedmember_external_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='storedmembercontact',
            name='external_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID in old DB'),
        ),
    ]