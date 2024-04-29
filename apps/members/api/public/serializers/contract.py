import functools

from django.db import models, transaction

from rest_framework import serializers

from sentry_sdk.integrations.wsgi import get_client_ip

from apps.campaigns.models import LevelInstance
from apps.core.api.serializers import ModelBaseSerializer
from apps.members import services
from apps.members.models import Contract


class ContractSignSerializer(ModelBaseSerializer):
    """Represent serializer for member/unregister member to sign contracts."""

    level_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
    )

    class Meta:
        model = Contract
        fields = (
            "signature",
            "level_ids",
        )
        extra_kwargs = {
            "signature": {"required": True, "allow_blank": False},
        }

    def validate(self, attrs: dict) -> dict:
        attrs = super().validate(attrs)
        level_ids = attrs.get("level_ids", [])
        contract = self.instance
        errors = services.validate_available_levels(
            LevelInstance.objects.filter(
                contract=contract,
                id__in=level_ids,
            ).annotate(
                index=models.Case(
                    *[
                        models.When(id=instance.id, then=idx)
                        for idx, instance in enumerate(
                            contract.levels.order_by("id"),
                        )
                    ],
                    output_field=models.IntegerField(),
                ),
            ),
        )
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def save(self, **kwargs):
        """Sign contract and send notification."""
        signed_contract = services.sign_contract(
            contract=self.instance,
            data=self.validated_data,
            ip_address=get_client_ip(self._request.META),
        )
        transaction.on_commit(
            functools.partial(
                services.send_contract_approval_review_email,
                contract_id=signed_contract.id,
            ),
        )
        return signed_contract
