from rest_framework import serializers

from apps.core.api.serializers import (
    ModelBaseSerializer,
    PhoneField,
    ZIPCodeRegexField,
)
from apps.members.models import Member


class MemberReadSerializer(ModelBaseSerializer):
    """Serializer for Member model with list and retrieve methods."""

    work_phone = PhoneField(required=True, allow_blank=True)
    mobile_phone = PhoneField(required=True, allow_blank=True)
    stored_member_id = serializers.IntegerField(allow_null=True, default=None)
    zipcode = ZIPCodeRegexField(required=True, allow_blank=False)

    class Meta:
        model = Member
        fields = (
            "stored_member_id",
            "name",
            "address",
            "city",
            "state",
            "zipcode",
            "first_name",
            "last_name",
            "email",
            "work_phone",
            "mobile_phone",
        )
