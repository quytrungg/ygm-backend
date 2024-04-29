# Generated by Django 4.2.7 on 2023-12-07 06:39

from django.db import migrations, models


def populate_user_campaign_is_active(apps, schema_editor):
    """Set user campaigns to inactive for `done` campaign."""
    UserCampaign = apps.get_model("campaigns.UserCampaign")
    UserCampaign.objects.filter(campaign__status="done").update(
        is_active=False,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0038_alter_usercampaign_preferred_contact_methods'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercampaign',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Is active'),
        ),
        migrations.RunPython(
            populate_user_campaign_is_active,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
