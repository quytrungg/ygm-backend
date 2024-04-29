from django.conf import settings
from django.utils.translation import gettext_lazy as _

from libs.notifications.email import DefaultEmailNotification


class UserPasswordResetEmailNotification(DefaultEmailNotification):
    """Used to send email with password reset link."""

    subject = _("Password Reset")
    template = "users/emails/password_reset.html"

    def __init__(self, user, **template_context) -> None:
        super().__init__(**template_context)
        self.user = user

    def get_recipient_list(self) -> list:
        """Get email's recipients."""
        return [self.user.email]

    def get_template_context(self) -> dict:
        """Get email's template context."""
        self.template_context.update(
            new_password_url=settings.FRONTEND_URL + settings.NEW_PASSWORD_URL,
            app_label=settings.APP_LABEL,
        )
        return self.template_context
