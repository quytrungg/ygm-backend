from functools import partial

from django.db import transaction

from rest_framework import serializers

from apps.chambers.api.common.serializers import (
    BaseChamberWriteSerializer,
    CreateCEOAdminMixin,
)
from apps.core.api.serializers import BaseSerializer, make_field_read_only
from apps.users.constants import UserRole
from apps.users.tasks import send_welcome_chamber_admin_email

from ....models import Chamber
from ...common.validators import CeoSameAsCoordValidator


class DashboardDataSerializer(BaseSerializer):
    """Represent single CA dashboard data.

    Data have the format of a dictionary:
        - current: integer
        - total: integer

    """

    current = serializers.IntegerField()
    total = serializers.IntegerField()

    class Meta:
        fields = (
            "current",
            "total",
        )

    def create(self, validated_data) -> None:
        """Bypass check."""

    def update(self, instance, validated_data) -> None:
        """Bypass check."""


class DashboardSerializer(BaseSerializer):
    """Serializer for Chamber admin dashboard."""

    # TODO: Modify this after planning
    campaign_goal = DashboardDataSerializer()
    volunteers = DashboardDataSerializer()
    members = DashboardDataSerializer()
    inventory = DashboardDataSerializer()

    class Meta:
        fields = (
            "campaign_goal",
            "volunteers",
            "members",
            "inventory",
        )

    def create(self, validated_data) -> None:
        """Bypass check."""

    def update(self, instance, validated_data) -> None:
        """Bypass check."""


class ChamberUpdateSerializer(
    CreateCEOAdminMixin,
    BaseChamberWriteSerializer,
):
    """Update Chamber information, for chamber admin."""

    def __init__(self, *args, **kwargs):
        """Allow only super admin to update trc coordinator info.

        If chamber has `ceo_email` set, we allow only SA to update CEO admin.

        """
        super().__init__(*args, **kwargs)
        if (
            self._request.auth
            and self._request.auth.user.role != UserRole.SUPER_ADMIN
        ):
            for coord_field_name in self.Meta.trc_coord_fields:
                make_field_read_only(self.fields[coord_field_name])
            if self.instance.ceo_email:
                for ceo_field_name in self.Meta.ceo_info_conf:
                    make_field_read_only(self.fields[ceo_field_name])

    class Meta(CreateCEOAdminMixin.Meta, BaseChamberWriteSerializer.Meta):
        model = Chamber
        trc_coord_fields = (
            "trc_coord_first_name",
            "trc_coord_last_name",
            "trc_coord_phone",
            "trc_coord_title",
            "trc_coord_office_phone",
            "trc_coord_office_phone_ext",
        )
        fields = BaseChamberWriteSerializer.Meta.fields + trc_coord_fields + (
            "instagram_url",
            "facebook_url",
            "twitter_url",
            "linkedin_url",
            "youtube_url",
            "subdomain",
            "trc_coord_email",
        )
        extra_kwargs = {
            "subdomain": {"read_only": True},
            "trc_coord_email": {"read_only": True},
        }
        validators = (CeoSameAsCoordValidator(),)

    def update(self, instance, validated_data):
        """Update chamber and its admin info.

        - Update coord admin info if current original user is SA.
        - Create/update CEO admin (can't update `ceo_email` if chamber already
        has it set).

        """
        ceo_email = instance.ceo_email or validated_data.get("ceo_email", "")
        validated_data["ceo_email"] = ceo_email
        updated_instance: Chamber = super().update(instance, validated_data)
        if self._request.auth.user.role == UserRole.SUPER_ADMIN:
            coord_admin = updated_instance.users.filter(
                email=updated_instance.trc_coord_email,
                role=UserRole.CHAMBER_ADMIN,
            ).first()
            coord_admin.first_name = updated_instance.trc_coord_first_name
            coord_admin.last_name = updated_instance.trc_coord_last_name
            coord_admin.save()

        if not ceo_email or ceo_email == updated_instance.trc_coord_email:
            return updated_instance

        ceo_admin = updated_instance.users.filter(
            email=updated_instance.ceo_email,
            role=UserRole.CHAMBER_ADMIN,
        ).first()
        if not ceo_admin:
            ceo_admin = self.create_ceo_admin(
                validated_data,
                chamber=updated_instance,
            )
            transaction.on_commit(
                partial(
                    send_welcome_chamber_admin_email.delay,
                    chamber_admin_id=ceo_admin.id,
                ),
            )
        else:
            ceo_admin.first_name = updated_instance.ceo_first_name
            ceo_admin.last_name = updated_instance.ceo_last_name
            ceo_admin.mobile_phone = updated_instance.ceo_phone
            ceo_admin.save()
        return updated_instance

    def create(self, validated_data):
        """Disallow using this serializer to create."""
        raise NotImplementedError("Unsupported operation")
