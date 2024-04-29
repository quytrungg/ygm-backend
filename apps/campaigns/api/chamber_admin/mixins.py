from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from apps.campaigns.models import UserCampaign
from apps.users.models import User


class UserCampaignEmailValidationMixin:
    """Mixin to validate campaign user's email."""

    def validate_email(self, email: str) -> str:
        """Validate email against our restrictions.

        If no user's account uses the email yet, we skip further validation.
        If there's an account using the email, we don't allow it to be used if:
            - it's admin account
            - or the email belongs to account of another chamber
            - or there is already a UserCampaign instance with this email in
            the current campaign.

        """
        campaign = self.context["request"].campaign
        error_msg = "Account with this email already exists"
        self.existing_account = User.objects.filter(
            email=email,
        ).first()
        if not self.existing_account:
            return email

        admin_roles = (
            User.ROLES.SUPER_ADMIN,
            User.ROLES.CHAMBER_ADMIN,
        )
        if self.existing_account.role in admin_roles:
            raise serializers.ValidationError(
                _(error_msg),
            )

        account_existed_in_current_chamber = (
            self.existing_account.chamber_id == campaign.chamber_id
        )
        if not account_existed_in_current_chamber:
            raise serializers.ValidationError(
                _(error_msg),
            )

        user_existed_in_current_campaign = (
            UserCampaign.objects.filter(
                email=email,
                campaign_id=campaign.id,
            ).exists()
        )

        if user_existed_in_current_campaign:
            raise serializers.ValidationError(
                _(error_msg),
            )
        return email
