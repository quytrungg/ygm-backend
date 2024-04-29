from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from libs.notifications.email import DefaultEmailNotification

from apps.campaigns.utils import get_chamber_url
from apps.users.models import User


class VolunteerInvitationEmailNotification(DefaultEmailNotification):
    """Send invitation email to campaign's volunteer."""

    subject = _("Welcome new volunteer")
    template = "campaigns/emails/volunteer_invitation.html"

    def __init__(self, volunteer: User, campaign, **template_context):
        super().__init__(**template_context)
        self.campaign = campaign
        self.volunteer = volunteer
        self.chamber = self.volunteer.chamber
        self.volunteer_registration_url = (
            f"{get_chamber_url(self.chamber)}/auth/register"
        )

    def get_recipient_list(self) -> list[str]:
        """Return volunteer email."""
        return [self.volunteer.email]

    def get_template_context(self) -> dict:
        """Provide additional context about current volunteer."""
        ctx = super().get_template_context()
        chamber_admin: User = self.chamber.users.filter(
            role=User.ROLES.CHAMBER_ADMIN,
        ).first()
        ctx.update(
            uid=urlsafe_base64_encode(force_bytes(self.volunteer.pk)),
            token=PasswordResetTokenGenerator().make_token(self.volunteer),
            volunteer=self.volunteer,
            chamber=self.chamber,
            chamber_admin=chamber_admin,
            campaign=self.campaign,
            app_label=settings.APP_LABEL,
            registration_url=self.volunteer_registration_url,
        )
        return ctx

    def get_formatted_subject(self) -> str:
        """Return email subject."""
        return f"{self.chamber.name} Sign-Up"
