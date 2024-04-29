from functools import partial

from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from drf_spectacular.utils import extend_schema_serializer

from libs.open_api.serializers import OpenApiSerializer

from apps.chambers.services import generate_default_timelines
from apps.core.api.serializers import (
    BaseSerializer,
    ModelBaseSerializer,
    StringOptionSerializer,
)
from apps.users.models import User
from apps.users.tasks import send_welcome_chamber_admin_email

from ....constants import ChamberRenewConfig
from ....models import Chamber
from ...common.serializers import (
    BaseChamberWriteSerializer,
    CreateCEOAdminMixin,
)
from ...common.validators import (
    CeoSameAsCoordValidator,
    ChamberAdminEmailValidator,
)
from .branding import (
    ChamberBrandingSerializer,
    ChamberBrandingUpdateSerializer,
)


class ListChamberSerializer(ModelBaseSerializer):
    """Represent simple information of Chamber."""

    sales = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = Chamber
        fields = (
            "id",
            "nickname",
            "can_renew_campaign",
            "trc_coord_first_name",
            "trc_coord_last_name",
            "trc_coord_email",
            "phone",
            "sales",
        )


class ChamberDetailSerializer(ModelBaseSerializer):
    """Represent Chamber detail information, for super admin."""

    branding = ChamberBrandingUpdateSerializer()

    class Meta:
        model = Chamber
        fields = (
            "id",
            "subdomain",
            "can_renew_campaign",
            "trc_coord_first_name",
            "trc_coord_last_name",
            "trc_coord_email",
            "phone",
            "note",
            "name",
            "branding",
        )


class ChamberCreateSerializer(
    CreateCEOAdminMixin,
    BaseChamberWriteSerializer,
):
    """Serializer for super admin to create Chamber."""

    nickname = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=Chamber.objects.all())],
    )
    branding = ChamberBrandingSerializer(required=False)

    class Meta(CreateCEOAdminMixin.Meta, BaseChamberWriteSerializer.Meta):
        fields = BaseChamberWriteSerializer.Meta.fields + (
            "name",
            "nickname",
            "subdomain",
            "note",
            "trc_coord_email",
            "branding",
            "trc_coord_first_name",
            "trc_coord_last_name",
            "trc_coord_phone",
            "trc_coord_title",
            "trc_coord_office_phone",
            "trc_coord_office_phone_ext",
        )
        extra_kwargs = {
            "trc_coord_first_name": {"required": True, "allow_blank": False},
            "trc_coord_last_name": {"required": True, "allow_blank": False},
            "trc_coord_phone": {"required": True, "allow_blank": False},
            "trc_coord_title": {"required": False, "allow_blank": True},
            "subdomain": {"required": True},
            "trc_coord_email": {
                "validators": (ChamberAdminEmailValidator(),),
            },
            "ceo_email": {
                "validators": (ChamberAdminEmailValidator(),),
            },
        }
        validators = (CeoSameAsCoordValidator(),)

    def create(self, validated_data: dict) -> Chamber:
        """Create chamber, together with its branding and admin."""
        branding_data = validated_data.pop("branding", {})
        chamber = super().create(validated_data)
        branding_data["chamber"] = chamber
        branding_serializer = self.fields["branding"]
        branding_serializer.create(branding_data)
        trc_coord_admin = User(
            email=chamber.trc_coord_email,
            first_name=chamber.trc_coord_first_name,
            last_name=chamber.trc_coord_last_name,
            mobile_phone=chamber.trc_coord_phone,
            chamber=chamber,
            role=User.ROLES.CHAMBER_ADMIN,
        )
        trc_coord_admin.set_unusable_password()
        trc_coord_admin.save()
        ceo_admin = self.create_ceo_admin(validated_data, chamber=chamber)
        chamber.refresh_from_db()
        for admin in (trc_coord_admin, ceo_admin):
            if admin:
                transaction.on_commit(
                    partial(
                        send_welcome_chamber_admin_email.delay,
                        chamber_admin_id=admin.id,
                    ),
                )
        generate_default_timelines(chamber)
        return chamber

    def update(self, instance, validated_data):
        """Disallow using this serializer to update."""
        raise NotImplementedError("Unsupported operation")


@extend_schema_serializer(component_name="ChamberUpdateSA")
class ChamberUpdateSerializer(ModelBaseSerializer):
    """Update Chamber information, for super admin."""

    branding = ChamberBrandingUpdateSerializer(required=False)

    class Meta:
        model = Chamber
        fields = (
            "subdomain",
            "trc_coord_first_name",
            "trc_coord_last_name",
            "phone",
            "note",
            "branding",
        )
        extra_kwargs = {
            "subdomain": {"required": True},
        }

    def update(self, instance, validated_data):
        """Update chamber and its branding + chamber coord admin."""
        branding_data = validated_data.pop("branding", None)
        updated_instance: Chamber = super().update(instance, validated_data)
        chamber_coord_admin = updated_instance.users.filter(
            role=User.ROLES.CHAMBER_ADMIN,
            email=updated_instance.trc_coord_email,
        ).first()
        chamber_coord_admin.first_name = updated_instance.trc_coord_first_name
        chamber_coord_admin.last_name = updated_instance.trc_coord_last_name
        chamber_coord_admin.save()
        if branding_data is not None:
            branding_serializer = self.fields["branding"]
            branding_serializer.update(
                updated_instance.branding,
                branding_data,
            )
        return updated_instance

    def create(self, validated_data):
        """Disallow using this serializer to create."""
        raise NotImplementedError("Unsupported operation")


class ChamberDeleteVerifySerializer(BaseSerializer):
    """Verify password to delete Chamber."""

    password = serializers.CharField(required=True)

    def validate_password(self, password: str) -> str:
        """Validate password with current super-admin password."""
        if not self._user.check_password(password):
            raise serializers.ValidationError(_("Invalid password"))
        return password

    def create(self, validated_data):
        """Bypass check."""

    def update(self, instance, validated_data):
        """Bypass check."""


class ChamberNicknameCheckSerializer(ModelBaseSerializer):
    """Check for Chamber nickname uniqueness."""

    nickname = serializers.CharField(required=True)

    class Meta:
        model = Chamber
        fields = (
            "id",
            "nickname",
        )


class ChamberStatisticsSerializer(BaseSerializer):
    """Serializer for Chamber statistics."""

    # TODO: Modify this after planning
    year = serializers.IntegerField(write_only=True, required=False)
    trc_goal = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
        read_only=True,
    )
    total_sale = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
        read_only=True,
    )
    business_purchasing = serializers.IntegerField(read_only=True)
    total_volunteers = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            "year",
            "trc_goal",
            "total_sale",
            "business_purchasing",
            "total_volunteers",
        )

    def create(self, validated_data):
        """Bypass check."""

    def update(self, instance, validated_data):
        """Bypass check."""


class ChamberRenewConfigSerializer(OpenApiSerializer):
    """Represent chamber's renew config, including campaign's name."""

    config = StringOptionSerializer(many=True)
    campaign_name = serializers.CharField()

    class Meta:
        fields = (
            "config",
            "campaign_name",
        )


class ChamberCampaignRenewSASerializer(OpenApiSerializer):
    """Represent choices for renewing a chamber's campaign."""

    name = serializers.CharField(
        required=True,
        allow_blank=False,
        write_only=True,
    )
    year = serializers.IntegerField(
        required=True,
        min_value=0,
        max_value=3000,
        write_only=True,
    )
    inventory = serializers.BooleanField(write_only=True)
    incentives = serializers.BooleanField(write_only=True)
    users = serializers.BooleanField(write_only=True)
    contracts = serializers.BooleanField(write_only=True)
    renew_campaign_id = serializers.IntegerField(read_only=True)

    class Meta:
        fields = tuple(choice[0] for choice in ChamberRenewConfig.choices) + (
            "name",
            "year",
            "renew_campaign_id",
        )
