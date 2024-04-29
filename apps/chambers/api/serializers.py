from functools import partial

from django.db import transaction

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from s3direct.api.fields import S3DirectUploadURLField

from apps.core.api.serializers import ModelBaseSerializer
from apps.users.constants import UserRole
from apps.users.models import User
from apps.users.tasks import send_welcome_chamber_admin_email

from ..models import Chamber, ChamberBranding
from .common.validators import (
    CeoSameAsCoordValidator,
    ChamberAdminEmailValidator,
)


class InvoiceChamberSerializer(ModelBaseSerializer):
    """Represent chamber information in invoice."""

    chamber_logo = S3DirectUploadURLField(
        source="branding.chamber_logo",
        read_only=True,
    )

    class Meta:
        model = Chamber
        fields = (
            "name",
            "nickname",
            "address",
            "city",
            "state",
            "zipcode",
            "trc_coord_office_phone",
            "trc_coord_office_phone_ext",
            "chamber_logo",
        )


class BaseChamberWriteSerializer(ModelBaseSerializer):
    """Specify common fields for write operations on Chamber model."""

    class Meta:
        model = Chamber
        fields = (
            "id",
            "address",
            "city",
            "state",
            "zipcode",
            "country",
            "mail_address",
            "mail_city",
            "mail_state",
            "mail_zipcode",
            "mail_country",
            "phone",
            "member_count",
            "city_population",
            "country_population",
            "msa_population",
            "total_budget",
            "total_membership_budget",
            "pre_income",
            "ceo_first_name",
            "ceo_last_name",
            "ceo_email",
            "ceo_phone",
        )


class ChamberBrandingSerializer(ModelBaseSerializer):
    """Serializer for ChamberBranding model."""

    chamber_logo = S3DirectUploadURLField(
        required=False,
        allow_null=True,
    )
    trc_logo = S3DirectUploadURLField(
        required=False,
        allow_null=True,
    )
    landing_bg = S3DirectUploadURLField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ChamberBranding
        fields = (
            "site_primary_color",
            "site_secondary_color",
            "site_alternate_color",
            "headline",
            "public_prelaunch_msg",
            "volunteer_prelaunch_msg",
            "chamber_logo",
            "trc_logo",
            "landing_bg",
        )
        extra_kwargs = {
            "site_primary_color": {"required": False, "allow_blank": True},
            "site_secondary_color": {"required": False, "allow_blank": True},
            "site_alternate_color": {"required": False, "allow_blank": True},
            "headline": {"required": False, "allow_blank": True},
            "public_prelaunch_msg": {
                "required": False,
                "allow_blank": True,
            },
            "volunteer_prelaunch_msg": {
                "required": False,
                "allow_blank": True,
            },
        }


# pylint: disable=abstract-method
class CreateCEOAdminMixin(serializers.Serializer):
    """Provide creation method for chamber CEO's admin."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (
            getattr(self.context.get("view"), "swagger_fake_view", False)
            or not getattr(self, "initial_data", None)  # for swagger check
        ):
            return

        ceo_fields = self.Meta.ceo_info_conf.keys()
        ceo_info_filled = any(
            self.initial_data.get(ceo_field) for ceo_field in ceo_fields
        )
        if not ceo_info_filled:
            return

        ceo_info_conf = self.Meta.ceo_info_conf
        for field_name, conf in ceo_info_conf.items():
            for attr, value in conf.items():
                setattr(self.fields[field_name], attr, value)

    def create_ceo_admin(self, data: dict, chamber: Chamber) -> User | None:
        """Create chamber admin from CEO's information (if available).

        If `ceo_email` == `trc_coord_email`, don't create ceo admin.

        """
        email = data.get("ceo_email")
        if not email or email == chamber.trc_coord_email:
            return None
        ceo_admin = User(
            email=data["ceo_email"],
            first_name=data["ceo_first_name"],
            last_name=data["ceo_last_name"],
            mobile_phone=data["ceo_phone"],
            role=UserRole.CHAMBER_ADMIN,
            chamber=chamber,
        )
        ceo_admin.set_unusable_password()
        ceo_admin.save()
        return ceo_admin

    class Meta:
        ceo_info_conf = {
            "ceo_email": {"required": True, "allow_blank": False},
            "ceo_first_name": {"required": True, "allow_blank": False},
            "ceo_last_name": {"required": True, "allow_blank": False},
            "ceo_phone": {"required": True, "allow_blank": True},
        }


class ChamberCreateSASerializer(
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
            role=UserRole.CHAMBER_ADMIN,
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
        return chamber

    def update(self, instance, validated_data):
        """Disallow using this serializer to update."""
        raise NotImplementedError("Unsupported operation")
