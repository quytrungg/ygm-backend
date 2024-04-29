import collections
from functools import partial

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from s3direct.api.fields import S3DirectUploadURLField

from libs.open_api.serializers import OpenApiSerializer

from apps.chambers import services as chambers_services
from apps.chambers.models import StoredMember
from apps.core.api.serializers import (
    CurrentCampaignDefault,
    ModelBaseSerializer,
)
from apps.core.exceptions import NonFieldValidationError
from apps.users.models import User

from ....constants import UserCampaignRole
from ....models import Team, UserCampaign
from ....tasks import send_volunteers_invitation_emails
from ...common.serializers.team import TeamSerializer
from ..mixins import UserCampaignEmailValidationMixin


class UserCampaignUpdateSerializer(
    UserCampaignEmailValidationMixin,
    ModelBaseSerializer,
):
    """Represent detail info of a campaign user."""

    avatar = S3DirectUploadURLField(required=False, allow_null=True)
    is_active = serializers.BooleanField(read_only=True)
    teams = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        allow_empty=True,
        many=True,
        write_only=True,
    )
    team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all().with_team_captain(),
        allow_null=True,
    )
    deactivated_at = serializers.DateTimeField(
        read_only=True,
    )
    managed_teams = TeamSerializer(many=True, read_only=True)
    contract_count = serializers.CharField(default="", read_only=True)

    class Meta:
        model = UserCampaign
        fields = (
            "id",
            "first_name",
            "last_name",
            "mobile_phone",
            "work_phone",
            "email",
            "role",
            "member",
            "team",
            "is_active",
            "avatar",
            "teams",
            "managed_teams",
            "deactivated_at",
            "contract_count",
        )
        extra_kwargs = {
            "role": {"required": True},
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not getattr(self.context["view"], "swagger_fake_view", False):
            instance = self.instance
            if (
                not instance
                or not instance.is_imported_user
                or instance.is_invitation_email_sent
            ):
                self.fields["email"].read_only = True

    def validate(self, attrs: dict) -> dict:
        """Validate data before updating user campaign instance.

        Chamber admin is not allowed to change role of himself and
        other chamber admins, only super admin can do that.

        Only teams that belong to the campaign are allowed to be assigned.

        If campaign can has vice chairs, only vice chairs can manage
            multiple teams.
        Else, if campaign doesn't has vice chairs, only chamber chairs can
            manage multiple teams.

        """
        validated_data = super().validate(attrs)
        if (
            self._request.auth.user.role == User.ROLES.CHAMBER_ADMIN
            and self.instance.role == UserCampaignRole.CHAMBER_ADMIN
        ):
            validated_data.pop("role", None)
        teams = validated_data.get("teams", [])
        teams = [
            team for team in teams
            if team.campaign_id == self.instance.campaign_id
        ]
        new_role = validated_data.get("role")
        campaign_has_vice_chairs = self.instance.campaign.has_vice_chairs
        disallow_vice_chair_management = (
            campaign_has_vice_chairs
            and new_role != UserCampaignRole.VICE_CHAIR
        )
        disallow_chamber_chair_management = (
            not campaign_has_vice_chairs
            and new_role != UserCampaignRole.CHAMBER_CHAIR
        )
        if disallow_vice_chair_management or disallow_chamber_chair_management:
            teams = []
        validated_data["teams"] = teams
        validated_data = self._populate_company_info_from_member(
            validated_data,
        )
        return validated_data

    def _populate_company_info_from_member(self, validated_data: dict) -> dict:
        """Set values for `company_*` fields using data from `member`."""
        member: StoredMember | None = validated_data.get("member")
        if not member:
            return validated_data

        validated_data.update({
            "company_name": member.name,
            "company_address": member.address,
            "company_city": member.city,
            "company_state": member.state,
            "company_zip_code": member.zip,
            "company_phone_number": member.phone,
        })
        return validated_data

    def _save_managed_teams(self, instance, teams):
        """Save managed teams for user campaign instance."""
        instance.managed_teams.set(teams)
        instance.save()

    def update(self, instance, validated_data) -> UserCampaign:
        """Update user campaign instance.

        Also update user's first name, last name, and mobile phone.

        """
        with transaction.atomic():
            teams = validated_data.pop("teams", [])
            if not instance.is_invitation_email_sent:
                transaction.on_commit(
                    partial(
                        send_volunteers_invitation_emails.delay,
                        [instance.id],
                    ),
                )
            updated_instance: UserCampaign = super().update(
                instance,
                validated_data,
            )
            chambers_services.add_stored_member_contact(
                stored_member=updated_instance.member,
                contact_info=updated_instance.contact_info,
            )
            self._save_managed_teams(updated_instance, teams)
            return updated_instance


class UserCampaignCreateSerializer(
    UserCampaignEmailValidationMixin,
    ModelBaseSerializer,
):
    """Create volunteer for a specific campaign."""

    existing_account: User

    campaign = serializers.HiddenField(
        default=CurrentCampaignDefault(),
    )
    team_manager = serializers.PrimaryKeyRelatedField(
        queryset=UserCampaign.objects.filter(
            role__in=(
                UserCampaignRole.VICE_CHAIR,
                UserCampaignRole.CHAMBER_CHAIR,
            ),
        ),
        allow_null=True,
        write_only=True,
    )
    team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all().with_team_captain(),
        allow_null=True,
    )

    class Meta:
        model = UserCampaign
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "role",
            "team_manager",
            "team",
            "campaign",
            "member",
            "work_phone",
            "mobile_phone",
        )
        extra_kwargs = {
            "role": {"required": True},
            "member": {"required": True, "allow_null": False},
        }

    def create(self, validated_data: dict) -> UserCampaign:
        """Create the volunteer and its account."""
        campaign = validated_data.pop("campaign")
        team_manager = validated_data.pop("team_manager", None)
        team = validated_data.pop("team", None)
        member = validated_data.pop("member")
        user_campaign_role = validated_data.pop("role")
        if not self.existing_account:
            self.existing_account = User(
                **validated_data,
                role=User.ROLES.VOLUNTEER,
                chamber_id=campaign.chamber_id,
            )
            self.existing_account.set_unusable_password()
        else:
            for field, value in validated_data.items():
                setattr(self.existing_account, field, value)
        self.existing_account.save()
        validated_data["user"] = self.existing_account
        validated_data["role"] = user_campaign_role
        validated_data["campaign"] = campaign
        validated_data["team"] = team
        validated_data["member"] = member
        user_campaign: UserCampaign = super().create(validated_data)
        chambers_services.add_stored_member_contact(
            stored_member=user_campaign.member,
            contact_info=user_campaign.contact_info,
        )
        transaction.on_commit(
            partial(
                send_volunteers_invitation_emails.delay,
                [user_campaign.id],
            ),
        )
        if team and team_manager:
            team.managed_by = team_manager
            team.save()
        return user_campaign

    def validate(self, attrs: dict) -> dict:
        """Validate data before creating user campaign instance.

        Team is required for volunteers.
        Team and vice chair is required for team captains.

        """
        team = attrs.get("team")
        team_manager = attrs.get("team_manager")
        team_manager_role = team_manager.role if team_manager else None
        campaign = attrs["campaign"]
        errors = {}
        if (
            attrs["role"] == UserCampaignRole.VOLUNTEER
            and not team
        ):
            errors["team"] = _("Team is required for volunteers.")
        if (
            campaign.has_vice_chairs
            and team_manager
            and team_manager_role == UserCampaignRole.CHAMBER_CHAIR
        ):
            errors["team_manager"] = _(
                "Team manager in campaign that has vice chairs "
                "can't be chair.",
            )
        if (
            not campaign.has_vice_chairs
            and team_manager
            and team_manager_role == UserCampaignRole.VICE_CHAIR
        ):
            errors["team_manager"] = _(
                "Team manager in campaign that does not have vice "
                "chairs can't be vice chair.",
            )

        if (
            attrs["role"] == UserCampaignRole.TEAM_CAPTAIN
            and (not team or not team_manager)
        ):
            errors["team"] = _("Team is required for team captains.")
            errors["team_manager"] = _(
                "Vice chair is required for team captains.",
            )
        if team and team.campaign_id != campaign.id:
            errors["team"] = _("Team does not exist in campaign.")
        if team_manager and team_manager.campaign_id != campaign.id:
            errors["team_manager"] = _("Vice chair doesn't exist in campaign.")

        if errors:
            raise serializers.ValidationError(errors)
        return super().validate(attrs)


class UserCampaignAssignTeamSerializer(OpenApiSerializer):
    """Serializer to assign users to chosen team."""

    ids = serializers.ListField(
        child=serializers.IntegerField(),
    )
    team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all().with_team_captain(),
    )

    class Meta:
        model = UserCampaign
        fields = (
            "ids",
            "team",
        )

    def validate(self, attrs):
        """Validate selected users and selected team."""
        campaign = self.context["request"].campaign
        user_ids = attrs.get("ids", [])
        team_prefetch_obj = Prefetch(
            "team",
            queryset=Team.objects.all().with_team_captain(),
        )
        users = UserCampaign.objects.filter(
            id__in=user_ids,
            campaign_id=campaign.id,
        ).prefetch_related(team_prefetch_obj)
        role_counter = collections.Counter(
            [user.role for user in users],
        )
        if role_counter[UserCampaignRole.TEAM_CAPTAIN] > 1:
            raise serializers.ValidationError(
                _("Can't assign multiple captains to 1 team."),
            )
        attrs["users"] = users
        team = attrs["team"]
        if team.campaign_id != campaign.id:
            raise serializers.ValidationError(
                _("Team does not exist in campaign."),
            )
        return attrs

    def save(self, **kwargs):
        """Check if selected users are validated to assign new team."""
        users = self.validated_data.pop("users", [])
        team = self.validated_data.pop("team", None)
        error_messages = []
        for user in users:
            user.team = team
            try:
                user.clean()
            except DjangoValidationError as exc:
                error_messages.extend(exc.messages)
        if error_messages:
            raise NonFieldValidationError(error_messages)
        UserCampaign.objects.bulk_update(users, fields=("team",))
