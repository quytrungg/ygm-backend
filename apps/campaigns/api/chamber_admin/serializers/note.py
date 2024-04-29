from django.template import Context, Template, TemplateSyntaxError

from rest_framework import serializers

from apps.core.api.serializers import ModelBaseSerializer

from ....models import Note


class NoteSerializer(ModelBaseSerializer):
    """Serializer for Note model."""

    campaign = serializers.IntegerField(
        source="campaign.id",
        read_only=True,
    )
    type = serializers.CharField(read_only=True)
    modified_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Note
        fields = (
            "id",
            "type",
            "body",
            "campaign",
            "created",
            "modified_by",
            "context_variables",
        )

    def validate_body(self, value):
        """Validate that the body is valid django template."""
        try:
            Template(value).render(Context({}))
        except TemplateSyntaxError as error:
            raise serializers.ValidationError(
                f"Invalid note body: {error}",
            )
        return value
