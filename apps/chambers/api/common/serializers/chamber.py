from rest_framework import serializers

from apps.core.api.serializers import ModelBaseSerializer
from apps.users.models import User

from ....models import Chamber


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
            role=User.ROLES.CHAMBER_ADMIN,
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
