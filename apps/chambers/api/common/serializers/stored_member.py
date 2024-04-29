from rest_framework import serializers

from apps.core.api.serializers import (
    CurrentChamberDefault,
    ModelBaseSerializer,
)

from ....models import StoredMember
from .stored_member_contact import StoredMemberContactSerializer


class StoredMemberSerializer(ModelBaseSerializer):
    """Serializer to represent Stored Members."""

    chamber_id = serializers.HiddenField(
        default=CurrentChamberDefault(),
    )
    contacts = StoredMemberContactSerializer(many=True, allow_empty=True)

    class Meta:
        model = StoredMember
        fields = (
            "id",
            "chamber_id",
            "name",
            "address",
            "city",
            "state",
            "zip",
            "contacts",
        )

    def validate(self, attrs: dict) -> dict:
        """Perform extra validation."""
        name = attrs["name"]
        if not self.instance or self.instance.name != name:
            if StoredMember.objects.filter(
                chamber_id=attrs["chamber_id"],
                name=name,
            ).exists():
                raise serializers.ValidationError(
                    {
                        "name": "Member with this name already exists.",
                    },
                )
        return super().validate(attrs)

    def create(self, validated_data):
        """Create member and contacts."""
        contacts_data = validated_data.pop("contacts", [])
        member = super().create(validated_data)
        for contact_data in contacts_data:
            contact_data["stored_member"] = member
        contacts_serializer = self.fields["contacts"]
        contacts_serializer.create(contacts_data)
        return member

    def update(self, instance, validated_data):
        """Update member and contacts."""
        contacts_data = validated_data.pop("contacts", [])
        updated_member = super().update(instance, validated_data)
        for contact_data in contacts_data:
            contact_data["stored_member"] = updated_member
        contacts_serializer = self.fields["contacts"]
        contacts_serializer.update(
            updated_member.contacts.all(),
            contacts_data,
        )
        return updated_member
