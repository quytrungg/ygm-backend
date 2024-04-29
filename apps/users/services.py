from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from . import models, notifications


def reset_user_password(
    user: models.User,
) -> bool:
    """Reset user password.

    This will send to user an email with a link where user can enter new
    password.

    """
    return notifications.UserPasswordResetEmailNotification(
        user=user,
        uid=urlsafe_base64_encode(force_bytes(user.pk)),
        token=PasswordResetTokenGenerator().make_token(user),
    ).send()
