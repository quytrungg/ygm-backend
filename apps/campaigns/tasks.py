# pylint: disable=unused-argument
from django.db import models
from django.dispatch import receiver

from safedelete import HARD_DELETE

from config.celery import app

from apps.campaigns.context_managers import get_context_manager
from apps.members.models import Contract

from .constants import NoteType
from .models import Campaign, LevelInstance, Note, Product, UserCampaign
from .notifications import VolunteerInvitationEmailNotification


@app.task
def send_volunteers_invitation_emails(user_campaign_ids: list[int]):
    """Send invitation emails to volunteers."""
    user_campaigns = UserCampaign.objects.filter(
        id__in=user_campaign_ids,
    ).select_related("user__chamber", "campaign")

    for user_campaign in user_campaigns:
        invitation_email = VolunteerInvitationEmailNotification(
            volunteer=user_campaign.user,
            campaign=user_campaign.campaign,
        )
        invitation_email.send()


@receiver(models.signals.post_save, sender=Campaign)
def create_notes_on_campaign_create(sender, instance, created, **kwargs):
    """Generate notes on Campaign Creation."""
    if not created:
        return
    notes = [
        Note(
            type=note_type.value,
            campaign=instance,
            body=get_context_manager(note_type).get_default_template(),
        ) for note_type in NoteType
    ]
    Note.objects.bulk_create(notes)


@receiver(models.signals.post_save, sender=Product)
def update_products_without_renew_included(
    sender,
    instance,
    created,
    **kwargs,
):
    """Remove levels and contracts with products not included in renewal."""
    campaign = instance.category.campaign
    if (
        created
        or not campaign.status == Campaign.STATUSES.RENEWAL
        or instance.is_included_in_renewal
    ):
        return
    LevelInstance.objects.filter(
        level__product_id=instance.id,
        contract__status=Contract.STATUSES.DRAFT,
    ).delete(force_policy=HARD_DELETE)
    Contract.objects.filter(
        campaign_id=campaign.id,
        levels__isnull=True,
        status=Contract.STATUSES.DRAFT,
    ).delete()
