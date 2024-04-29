from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from libs.notifications.email import DefaultEmailNotification

from apps.campaigns.utils import get_chamber_url


class WelcomeChamberAdminEmailNotification(DefaultEmailNotification):
    """Used to send welcome email to new chamber admin."""

    subject = _("Welcome new Chamber Admin")
    template = "chambers/emails/welcome_chamber_admin.html"

    def __init__(self, chamber_admin, **template_context):
        super().__init__(**template_context)
        self.chamber_admin = chamber_admin
        self.chamber_admin_registration_url = (
            f"{get_chamber_url(self.chamber_admin.chamber)}"
            f"/admin/auth/register"
        )

    def get_recipient_list(self) -> list[str]:
        """Return chamber's TRC coordinator email."""
        return [self.chamber_admin.email]

    def get_template_context(self) -> dict:
        """Provide additional context about current chamber admin."""
        ctx = super().get_template_context()
        ctx.update(
            uid=urlsafe_base64_encode(force_bytes(self.chamber_admin.pk)),
            token=PasswordResetTokenGenerator().make_token(self.chamber_admin),
            chamber_admin=self.chamber_admin,
            chamber=self.chamber_admin.chamber,
            app_label=settings.APP_LABEL,
            registration_url=self.chamber_admin_registration_url,
        )
        return ctx
