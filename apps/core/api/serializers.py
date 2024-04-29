import copy
import typing
from collections import abc

from django.utils.translation import gettext_lazy

from rest_framework import request, serializers

from ordered_model.serializers import OrderedModelSerializer
from timezone_field.rest_framework import TimeZoneSerializerField

from apps.campaigns.services import get_chamber_newest_campaign
from apps.chambers.models import Chamber

from ..constants import AvailableTimezone


# pylint: disable=abstract-method
class BaseSerializer(serializers.Serializer):
    """Serializer with common logic."""

    def __init__(self, *args, **kwargs):
        """Set current user."""
        super().__init__(*args, **kwargs)
        self._request: request.Request = self.context.get("request")
        self._user = getattr(self._request, "user", None)

    @property
    def _meta(self):
        """Get `Meta` class.

        Used to avoid adding `pylint: disable=no-member`

        """
        # pylint: disable=no-member
        return self.Meta


class ModelBaseSerializer(BaseSerializer, serializers.ModelSerializer):
    """Model Serializer with common logic."""

    def get_instance(self, attrs: dict):
        """Get instance depending on request."""
        if self.instance:  # if it's update request
            return copy.deepcopy(self.instance)
        # If attrs have `id` data, get instance form db
        # if it is a create request, we return empty instance
        instance_id = attrs.get("id")
        instance = self._meta.model.objects.filter(pk=instance_id).first()
        return instance or self._meta.model()

    def prepare_instance(self, attrs: dict):
        """Prepare instance depending on create/update.

        If `create` used, create empty instance and set fields' values with
        received data. If `update` used, update existing instance with received
        data.

        """
        # Prepare instance depending on create/update
        instance = self.get_instance(attrs)

        # skip creating/updating instance related objects
        relations = self._get_relations_fields_names()

        # Set new data for instance, while ignoring relations
        for attr, value in attrs.items():
            if attr not in relations:
                setattr(instance, attr, value)

        return instance

    def validate(self, attrs: dict) -> dict:
        """Call model's `.clean()` method during validation.

        Create:
            Just create model instance using provided data.
        Update:
            `self.instance` contains instance with new data. We apply passed
            data to it and then call `clean` method for this temp instance.

        """
        attrs = super().validate(attrs)

        instance = self.prepare_instance(attrs)

        instance.clean()

        return attrs

    def _get_relations_fields_names(self) -> set[str]:
        """Extract fields with relations before validation."""
        relations = set()

        # Remove related fields from validated data for future manipulations
        for _, field in self.fields.items():
            if field.read_only:
                continue

            if "." in field.source:
                source_attr = field.source.split(".")[0]
                relations.add(source_attr)
                continue

            is_many_model_serializer = (
                isinstance(field, serializers.ListSerializer)
                and isinstance(field.child, serializers.ModelSerializer)
            )
            is_model_serializer = (
                isinstance(field, serializers.ModelSerializer)
            )
            is_m2m_serializer = (
                isinstance(field, serializers.ManyRelatedField)
            )
            if (
                is_many_model_serializer
                or is_model_serializer
                or is_m2m_serializer
            ):
                relations.add(field.source)

        return relations


class PhoneField(serializers.RegexField):
    """Custom serializer field for phone value."""

    def __init__(self, **kwargs):
        super().__init__(regex=r"^\d{9,15}$", **kwargs)


class CurrentCampaignDefault:
    """Get the campaign from user who makes request with post method."""

    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context["request"].campaign

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class CurrentUserCampaignDefault:
    """Get the current `UserCampaign` instance."""

    requires_context = True

    def __call__(self, serializer_field):
        """Return `UserCampaign` of current user and campaign."""
        campaign = serializer_field.context["request"].campaign
        user = serializer_field.context["request"].user
        return user.user_campaigns.filter(campaign=campaign).first()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class CurrentTimelineDefault:
    """Get the timeline from current campaign."""

    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context["request"].campaign.timeline

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class StringOptionSerializer(serializers.Serializer):
    """Represent option with string value."""

    value = serializers.CharField()
    label = serializers.CharField()

    class Meta:
        fields = (
            "value",
            "label",
        )

    def create(self, validated_data) -> None:
        """Bypass check."""

    def update(self, instance, validated_data) -> None:
        """Bypass check."""


class IntegerOptionSerializer(serializers.Serializer):
    """Represent option with integer value."""

    value = serializers.IntegerField()
    label = serializers.CharField()

    class Meta:
        fields = (
            "value",
            "label",
        )

    def create(self, validated_data) -> None:
        """Bypass check."""

    def update(self, instance, validated_data) -> None:
        """Bypass check."""


class CurrentChamberDefault:
    """Provide chamber from context."""

    requires_context = True

    def __call__(self, serializer_field):
        """Get chamber id from user."""
        return serializer_field.context["request"].user.chamber_id


def make_field_read_only(field: serializers.Field) -> serializers.Field:
    """Make a serializer field become read only."""
    field.read_only = True
    field.write_only = False
    field.required = False
    return field


class BaseReorderSerializer(OrderedModelSerializer):
    """Represent base serializer for reorder API."""

    class Meta:
        fields = (
            "id",
            "order",
        )

    def validate(self, attrs: dict) -> dict:
        attrs = super().validate(attrs)
        order = attrs.get("order")
        min_order = self.instance.get_ordering_queryset().get_min_order()
        max_order = self.instance.get_ordering_queryset().get_max_order()
        if not min_order <= order <= max_order:
            raise serializers.ValidationError("Invalid order.")
        return attrs


class CampaignPublicSerializer(BaseSerializer):
    """Serializer for filtering campaign in public APIs."""

    chamber = serializers.PrimaryKeyRelatedField(
        queryset=Chamber.objects.all(),
    )

    class Meta:
        fields = (
            "chamber",
        )

    def validate(self, attrs):
        """Validate the chamber id and return the campaign."""
        attrs["campaign"] = get_chamber_newest_campaign(attrs["chamber"])
        return attrs

    def create(self, validated_data):
        """Bypass check."""

    def update(self, instance, validated_data):
        """Bypass check."""


# pylint: disable=protected-access
class NestedCreateUpdateListSerializer(serializers.ListSerializer):
    """Provide default logic for creating/updating/deleting nested objects."""

    def create(self, validated_data: list[dict]):
        """Bulk create nested objects."""
        model_cls = self.child.Meta.model
        instances = []
        for data_item in validated_data:
            data_item.pop("id", None)
            instances.append(model_cls(**data_item))
        return model_cls._meta.default_manager.bulk_create(instances)

    def update(self, instance, validated_data):
        """Update nested objects.

        Objects with ids available in `validated_data` are updated.
        Objects with ids not available in `validated_data` are deleted.
        Data without `id` field are used to create new objects.

        """
        obj_mapping = {obj.id: obj for obj in instance}
        data_for_update = self.get_data_for_update(
            obj_mapping, validated_data,
        )
        data_for_insertion = self.get_data_for_insertion(
            obj_mapping, validated_data,
        )
        instances_for_deletion = self.get_instances_for_deletion(
            obj_mapping,
            validated_data,
        )

        created_instances = self.perform_insertion(
            data_for_insertion=data_for_insertion,
        )
        updated_instances = self.perform_update(
            data_for_update=data_for_update,
        )
        self.perform_deletion(instances_for_deletion=instances_for_deletion)

        return created_instances + updated_instances

    def get_data_for_update(self, instances_mapping, validated_data) -> dict:
        """Return data for update operation."""
        return {
            data["id"]: data
            for data in validated_data
            if "id" in data and data["id"] in instances_mapping
        }

    # pylint: disable=unused-argument
    def get_data_for_insertion(self, instances_mapping, validated_data):
        """Return data for create operation."""
        return [data for data in validated_data if "id" not in data]

    def get_instances_for_deletion(
        self,
        instances_mapping: dict,
        validated_data,
    ) -> dict[int, typing.Any]:
        """Return data for delete operation."""
        return {
            obj_id: obj
            for obj_id, obj in instances_mapping.items()
            if obj_id not in self.get_data_for_update(
                instances_mapping,
                validated_data,
            )
        }

    def perform_insertion(self, data_for_insertion: abc.Sequence[dict]):
        """Bulk create objects."""
        model_cls = self.child.Meta.model
        manager = model_cls._meta.default_manager
        return manager.bulk_create(
            [
                model_cls(**creation_data)
                for creation_data in data_for_insertion
            ],
        )

    def perform_update(self, data_for_update: dict):
        """Update objects."""
        model_cls = self.child.Meta.model
        manager = model_cls._meta.default_manager
        instances_for_update = [
            model_cls(**update_data)
            for update_data in data_for_update.values()
        ]
        manager.bulk_update(
            instances_for_update,
            fields=self.editable_fields,
        )
        return instances_for_update

    def perform_deletion(self, instances_for_deletion: dict):
        """Delete objects."""
        model_cls = self.child.Meta.model
        manager = model_cls._meta.default_manager
        return manager.filter(
            id__in=list(instances_for_deletion),
        ).delete()

    @property
    def editable_fields(self):
        """Return editable fields for update operation."""
        return (
            field.field_name
            for field in self.child._writable_fields
            if field.field_name not in ("id", "pk")
        )


class TimezoneChoiceField(TimeZoneSerializerField, serializers.ChoiceField):
    """Handle timezone values."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("choices", AvailableTimezone.choices)
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        """Return timezone object."""
        # this calls `to_internal_value` of `ChoiceField`
        data = super(TimeZoneSerializerField, self).to_internal_value(data)
        # this calls `to_internal_value` of `TimeZoneSerializerField`
        return super().to_internal_value(data)

    def to_representation(self, value):
        """Return the text repr of timezone."""
        # this calls `to_internal_value` of `TimeZoneSerializerField`
        value = super().to_representation(value)
        # this calls `to_internal_value` of `ChoiceField`
        return super(TimeZoneSerializerField, self).to_representation(value)


class ZIPCodeRegexField(serializers.RegexField):
    """Custom RegexField for validating ZIP code.

    We need a custom error message here.

    """

    default_error_messages = {
        "invalid": gettext_lazy("Invalid ZIP code"),
    }

    def __init__(self, **kwargs):
        super().__init__(regex=r"^\d{5}((-\d{1,4})|(\.0))?$", **kwargs)
