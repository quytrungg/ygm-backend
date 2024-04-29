from django.http import HttpResponse

from rest_framework import mixins
from rest_framework.decorators import action

from import_export_extensions.api.views import ImportJobViewSet

from apps.core.api.mixins import UpdateModelWithoutPatchMixin
from apps.core.api.permissions import AllowChamberAdmin
from apps.core.api.views import ChamberBaseViewSet

from .... import resources
from ....models import StoredMember
from ...common.serializers import StoredMemberSerializer
from .. import serializers


class StoredMemberViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    UpdateModelWithoutPatchMixin,
    mixins.DestroyModelMixin,
    ChamberBaseViewSet,
):
    """Provide Management for Stored Members."""

    queryset = StoredMember.objects.all()
    serializer_class = StoredMemberSerializer
    ordering_fields = (
        "name",
    )
    search_fields = (
        "name",
        "contact_first_name",
        "contact_last_name",
        "contact_email",
        "address",
    )

    def get_queryset(self):
        """Return only members within the chamber."""
        if getattr(self, "swagger_fake_view", False):
            return self.queryset.none()
        qs = super().get_queryset()
        return qs.filter(chamber_id=self.request.user.chamber_id)


class StoredMemberImportViewSet(ImportJobViewSet):
    """View to Import stored members data."""

    resource_class = resources.StoredMemberImportResource
    permission_classes = (AllowChamberAdmin,)
    ordering_fields = ("id",)
    search_fields = ("id",)
    serializer_class = serializers.StoredMemberImportJobSerializer

    def get_queryset(self):
        """Filter import jobs by resource used in viewset."""
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        return qs.filter(created_by=self.request.user)

    def get_resource_kwargs(self) -> dict:
        """Provide Chamber id from user."""
        return {"chamber_id": self.request.user.chamber_id}

    def get_serializer_class(self):
        """Return custom resource class for getting template action."""
        if self.action == "get_import_template":
            return serializers.StoredMemberImportFormatSerializer
        return super().get_serializer_class()

    @action(methods=("GET",), detail=False, url_path="template")
    def get_import_template(self, request, *args, **kwargs):
        """Return the import template."""
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        resource = resources.StoredMemberImportTemplateResource()
        file_format = serializer.validated_data["file_format"]
        export_data = file_format.export_data(resource.export())
        res = HttpResponse(
            export_data,
            content_type=file_format.get_content_type(),
        )
        res["Content-Disposition"] = (
            "attachment; "
            f"filename=MembersTableTemplate.{file_format.get_extension()}"
        )
        return res
