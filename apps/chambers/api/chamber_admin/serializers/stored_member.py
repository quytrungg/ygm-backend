from django.core.exceptions import ValidationError

from rest_framework import serializers

from import_export_extensions.api.serializers.import_job import (
    ImportProgressSerializer,
)
from import_export_extensions.models import ImportJob

from apps.core.api.serializers import BaseSerializer, ModelBaseSerializer

from .... import resources


class StoredMemberImportJobSerializer(ModelBaseSerializer):
    """Serializer for StoredMemberImportJob."""

    progress = ImportProgressSerializer()
    errors = serializers.SerializerMethodField()

    class Meta:
        model = ImportJob
        fields = (
            "id",
            "import_status",
            "data_file",
            "progress",
            "errors",
            "import_started",
            "import_finished",
            "created",
            "modified",
        )

    def _get_error_message_from_validation_error(
        self,
        error: ValidationError,
    ) -> list[str]:
        """Get error message from ValidationError."""
        error_messages = []
        for value in error.error_dict.values():
            error_messages.extend(
                [
                    message.message
                    for message in value
                ],
            )
        return error_messages

    def get_errors(self, job: ImportJob) -> dict[str, list[str]]:
        """Get errors from import job.

        Row index is increased by 1 to match the row number in the file.

        """
        if not (job.result and job.result.has_errors()):
            return {}

        job_errors = {}
        for row, errors in job.result.row_errors():
            row_errors = []
            for error in errors:
                if not isinstance(error, ValidationError):
                    row_errors.append(error.error)
                    continue
                row_errors.extend(
                    self._get_error_message_from_validation_error(error),
                )
            job_errors[row + 1] = row_errors
        return job_errors


class StoredMemberImportFormatSerializer(BaseSerializer):
    """Validate import format."""

    file_format = serializers.ChoiceField(
        choices=list(resources.SUPPORTED_FORMATS_MAP.keys()),
    )

    class Meta:
        fields = (
            "file_format",
        )

    def validate(self, attrs):
        """Return instance of the selected file format class."""
        attrs["file_format"] = resources.SUPPORTED_FORMATS_MAP[
            attrs["file_format"]
        ]()
        return attrs
