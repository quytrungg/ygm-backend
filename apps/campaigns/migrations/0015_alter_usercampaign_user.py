# Generated by Django 4.2.2 on 2023-09-07 09:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('campaigns', '0014_campaign_has_trades_campaign_has_vice_chairs_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercampaign',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_campaigns', to=settings.AUTH_USER_MODEL, verbose_name='Base User'),
        ),
    ]