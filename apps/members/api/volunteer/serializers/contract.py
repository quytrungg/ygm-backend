import functools

from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field

from apps.campaigns.api.common.serializers import UserCampaignCompactSerializer
from apps.campaigns.api.super_admin.serializers import CampaignSerializer
from apps.campaigns.models import Level, UserCampaign
from apps.chambers import services as chambers_services
from apps.chambers.api.common.serializers import StoredMemberSerializer
from apps.chambers.models import StoredMember
from apps.core.api.serializers import (
    BaseSerializer,
    CurrentUserCampaignDefault,
    ModelBaseSerializer,
)
from apps.members import services
from apps.members.models import Contract, Member

from ...common.serializers import (
    ContractLevelAttachMixin,
    ContractSelectedLevelSerializer,
    MemberReadSerializer,
)
from ...common.validators import ContractLevelsValidator, ContractTypeValidator


class LevelContractAttachSerializer(BaseSerializer):
    """Provide serializer to add products/levels."""

    level = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all().with_is_available(),
    )

    class Meta:
        fields = (
            "level",
        )

    def create(self, validated_data):
        """Bypass check."""

    def update(self, instance, validated_data):
        """Bypass check."""

    def validate(self, attrs):
        """Ensure level is still available."""
        attrs = super().validate(attrs)
        if not attrs["level"].is_available:
            raise serializers.ValidationError(
                _("This product is out of stock"),
            )
        return attrs


class ContractMemberSerializer(MemberReadSerializer):
    """Represent contract member in detail page."""

    stored_member = StoredMemberSerializer(read_only=True)

    class Meta(MemberReadSerializer.Meta):
        fields = MemberReadSerializer.Meta.fields + (
            "stored_member",
        )

    def validate(self, attrs: dict) -> dict:
        """Link the member to stored member if their names match."""
        stored_member_id = attrs["stored_member_id"]
        if stored_member_id:
            stored_member: StoredMember = StoredMember.objects.filter(
                chamber_id=self.context["request"].campaign.chamber_id,
                id=stored_member_id,
            ).first()
            if not stored_member:
                raise serializers.ValidationError(
                    {
                        "stored_member_id": _("Invalid stored member"),
                    },
                )
            if stored_member.name != attrs["name"]:
                raise serializers.ValidationError(
                    {
                        "name": _("Name does not match stored member's name."),
                    },
                )
        else:
            attrs["stored_member_id"] = getattr(
                StoredMember.objects.filter(
                    chamber_id=self.context["request"].campaign.chamber_id,
                    name=attrs["name"],
                ).first(),
                "id",
                None,
            )
        return attrs


class ContractDetailSerializer(ModelBaseSerializer):
    """Represent contract data, create and update contract."""

    campaign = CampaignSerializer(read_only=True)
    member = ContractMemberSerializer()
    levels = ContractSelectedLevelSerializer(many=True)
    shared_credits_with = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = (
            "id",
            "name",
            "type",
            "member",
            "status",
            "is_renewed",
            "note",
            "approved_at",
            "created_by",
            "levels",
            "shared_credits_with",
            "campaign",
        )
        extra_kwargs = {
            "approved_at": {"read_only": True},
            "is_renewed": {"read_only": True},
        }

    @extend_schema_field(UserCampaignCompactSerializer(many=True))
    def get_shared_credits_with(self, contract: Contract):
        """Return only shared volunteers."""
        return UserCampaignCompactSerializer(
            contract.shared_credits_with.exclude(id=contract.created_by_id),
            many=True,
        ).data


class ContractCreateUpdateSerializer(
    ContractLevelAttachMixin,
    ContractDetailSerializer,
):
    """Provide create/update functionalities for contract."""

    created_by = serializers.HiddenField(
        default=CurrentUserCampaignDefault(),
        required=False,
    )
    shared_credits_with = serializers.PrimaryKeyRelatedField(
        queryset=UserCampaign.objects.all(),
        many=True,
    )
    status = serializers.ChoiceField(
        choices=(Contract.STATUSES.DRAFT, Contract.STATUSES.SENT),
    )
    created_date = serializers.DateField(
        input_formats=("%m/%d/%Y",),
        write_only=True,
    )

    class Meta(ContractDetailSerializer.Meta):
        fields = ContractDetailSerializer.Meta.fields + (
            "created_date",
        )
        extra_kwargs = {
            "name": {"read_only": True},
        }
        validators = [
            ContractTypeValidator(),
            ContractLevelsValidator(),
        ]

    def validate(self, attrs: dict) -> dict:
        """Validate data.

        - Ensure all shared users are in the same campaign with contract's
        creator.

        """
        attrs = super().validate(attrs)
        contract_creator = attrs["created_by"]
        invalid_shared_users = services.get_contract_invalid_shared_volunteers(
            contract_creator=contract_creator,
            shared_volunteers=attrs["shared_credits_with"],
            contract_stored_member_id=attrs["member"]["stored_member_id"],
        )
        if invalid_shared_users:
            raise serializers.ValidationError(
                {"shared_credits_with": _("Invalid shared credits info")},
            )
        attrs["shared_credits_with"].append(contract_creator)
        return attrs

    def create(self, validated_data):
        """Create contract, member and attach selected levels."""
        member_data = validated_data.pop("member")
        levels_data = validated_data.pop("levels")
        created_date = validated_data.pop("created_date")
        member_serializer = self.fields["member"]
        member = member_serializer.create(member_data)
        contract_name = f"{member.name} {created_date.strftime('%m/%d/%Y')}"
        if duplicate_count := Contract.objects.filter(
            name__icontains=contract_name,
            campaign=self._request.campaign,
            created_by__user=self._user,
        ).count():
            contract_name = f"{contract_name} {duplicate_count}"
        validated_data["member"] = member
        validated_data["campaign"] = self._request.campaign
        validated_data["name"] = contract_name
        contract = super().create(validated_data)
        self.attach_levels_to_contract(contract, levels_data)
        return contract

    def update(self, instance, validated_data):
        """Update contract, member and selected levels."""
        member_data = validated_data.pop("member")
        levels_data = validated_data.pop("levels")
        member_serializer = self.fields["member"]
        member_serializer.update(instance.member, member_data)
        updated_contract = super().update(instance, validated_data)
        self.attach_levels_to_contract(updated_contract, levels_data)
        return updated_contract

    def save(self, **kwargs):
        """Send contract to member if needed."""
        is_update = self.instance is not None
        shared_volunteers = self.validated_data.pop("shared_credits_with")
        contract = super().save(**kwargs)
        services.set_contract_credits(
            contract=contract,
            shared_volunteers=shared_volunteers,
        )
        if services.need_send_contract(contract, is_update=is_update):
            transaction.on_commit(
                functools.partial(
                    services.send_contract,
                    contract_id=contract.id,
                ),
            )
            member: Member = contract.member
            if member.stored_member:
                contact_info = {
                    "first_name": member.first_name,
                    "last_name": member.last_name,
                    "email": member.email,
                    "work_phone": member.work_phone,
                    "mobile_phone": member.mobile_phone,
                }
                chambers_services.add_stored_member_contact(
                    stored_member=member.stored_member,
                    contact_info=contact_info,
                )
        return contract
