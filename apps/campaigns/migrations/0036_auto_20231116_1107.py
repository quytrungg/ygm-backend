# Generated by Django 4.2.7 on 2023-11-16 11:07

from django.db import migrations


def populate_missing_usercampaign(apps, schema_editor):
    """Populate missing `UserCampaign` for chamber admins."""
    Campaign = apps.get_model("campaigns", "Campaign")
    User = apps.get_model("users", "User")
    UserCampaign = apps.get_model("campaigns", "UserCampaign")
    chamber_admins = list(User.objects.filter(role="chamber_admin"))
    campaigns = list(Campaign.objects.all())
    existing_ca_usercampaigns = set(
        UserCampaign.objects.filter(
            user__role="chamber_admin",
        ).values_list("user_id", "campaign_id"),
    )
    new_usercampaigns = []
    for chamber_admin in chamber_admins:
        for campaign in campaigns:
            if (
                chamber_admin.chamber_id != campaign.chamber_id
                or (chamber_admin.id, campaign.id) in existing_ca_usercampaigns
            ):
                continue

            new_usercampaigns.append(
                UserCampaign(
                    user=chamber_admin,
                    campaign=campaign,
                    first_name=chamber_admin.first_name,
                    last_name=chamber_admin.last_name,
                    email=chamber_admin.email,
                    role="volunteer",
                ),
            )
    UserCampaign.objects.bulk_create(new_usercampaigns)


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0035_fix_start_date_data'),
    ]

    operations = [
        migrations.RunPython(
            populate_missing_usercampaign,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
