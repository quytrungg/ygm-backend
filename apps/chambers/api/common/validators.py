from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from apps.users.models import User


class CeoSameAsCoordValidator:
    """Validate CEO info are the same as TRC coordinator info."""

    requires_context = True

    def __call__(self, data, serializer):
        """Trigger different validation logic on create/update."""
        if serializer.instance is not None:
            self.validate_on_update(data, serializer)
        else:
            self.validate_on_create(data, serializer)

    def validate_on_create(self, data, serializer):
        """Validate data on chamber creation if 2 emails are the same."""
        if data.get("ceo_email") != data["trc_coord_email"]:
            return
        self.assert_ceo_same_as_trc_coord(data, serializer)

    def validate_on_update(self, data, serializer):
        """Validate data on chamber update if 2 emails are the same.

        Since we don't allow update `ceo_email` if it's already set, we
        prioritize getting its value from current chamber.

        """
        chamber = serializer.instance
        ceo_email = chamber.ceo_email or data.get("ceo_email", "")
        if ceo_email != chamber.trc_coord_email:
            return
        self.assert_ceo_same_as_trc_coord(data, serializer)

    def assert_ceo_same_as_trc_coord(self, data, serializer):
        """Assert all CEO's info are the same as TRC coordinator's info.

        If any ceo field is read only, we skip validation. This case happens
        when CA updates a chamber with `ceo_email` set.

        """
        field_pairs = (
            ("ceo_first_name", "trc_coord_first_name"),
            ("ceo_last_name", "trc_coord_last_name"),
            ("ceo_phone", "trc_coord_phone"),
        )
        errors = {}
        for ceo_field, trc_coord_field in field_pairs:
            if serializer.fields[ceo_field].read_only:
                # exit early, this means a CA is updating chamber which already
                # has `ceo_email` set
                break

            trc_coord_info = (
                data[trc_coord_field]
                if not serializer.fields[trc_coord_field].read_only
                else getattr(serializer.instance, trc_coord_field)
            )
            if data.get(ceo_field) != trc_coord_info:
                errors[ceo_field] = _(
                    "CEO information must be the same as TRC Coordinator's'.",
                )
        if errors:
            raise serializers.ValidationError(errors)


class ChamberAdminEmailValidator:
    """Validate email availability for chamber admin."""

    requires_context = True

    def __call__(self, email: str, serializer_field):
        """Check if the email is available for use."""
        user = User.all_objects.filter(email=email).first()
        if not user:
            return
        error = serializers.ValidationError(_("This field must be unique"))
        chamber = serializer_field.parent.instance
        if chamber is None:
            raise error
        if (
            user.chamber_id != chamber.id
            or user.role != User.ROLES.CHAMBER_ADMIN
        ):
            raise error
