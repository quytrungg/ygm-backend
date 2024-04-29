import collections

from rest_framework import serializers

from apps.core.api.serializers import (
    ModelBaseSerializer,
    NestedCreateUpdateListSerializer,
)

from ....models import StoredMemberContact


class StoredMemberContactListSerializer(NestedCreateUpdateListSerializer):
    """Provide creation/update/validation logic for list of StoredMember."""

    def to_internal_value(self, data):
        """Check if there's any duplicated contact email.

        Run check here to take advantage of existing conversion to
        `{parent_field}.{index}.{inner_field}` format.

        """
        value = super().to_internal_value(data)
        contact_emails_count_map = collections.Counter(
            [contact_info["email"] for contact_info in value],
        )
        errors = []
        for contact_info in value:
            if contact_emails_count_map[contact_info["email"]] > 1:
                errors.append(
                    {"email": "Contact's email should be unique."},
                )
            else:
                errors.append({})
        if any(errors):
            raise serializers.ValidationError(errors)
        return value


class StoredMemberContactSerializer(ModelBaseSerializer):
    """Represent a StoredMemberContact."""

    id = serializers.IntegerField(required=False)

    class Meta:
        model = StoredMemberContact
        list_serializer_class = StoredMemberContactListSerializer
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "work_phone",
            "mobile_phone",
        )
