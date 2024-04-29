from import_export import widgets
from import_export.formats import base_formats
from import_export.resources import ModelResource
from import_export.results import RowResult
from import_export_extensions.fields import Field
from import_export_extensions.resources import CeleryResourceMixin

from apps.chambers.models import StoredMember
from apps.core.import_export import formats as custom_formats
from apps.core.import_export import widgets as custom_widgets

from .services import add_stored_member_contact

SUPPORTED_IMPORT_FORMATS = [
    base_formats.CSV,
    custom_formats.XLSX,
    base_formats.XLS,
]
SUPPORTED_FORMATS_MAP = {
    fmt().get_extension(): fmt
    for fmt in SUPPORTED_IMPORT_FORMATS
}


class StoredMemberResource(ModelResource):
    """Resource for Stored Member Model."""

    name = Field(
        column_name="Company Name",
        attribute="name",
        widget=widgets.CharWidget(allow_blank=True, coerce_to_string=True),
    )
    address = Field(
        column_name="Company Address",
        attribute="address",
        default="",
        widget=widgets.CharWidget(allow_blank=True, coerce_to_string=True),
    )
    city = Field(
        column_name="City",
        attribute="city",
        default="",
        widget=widgets.CharWidget(allow_blank=True, coerce_to_string=True),
    )
    state = Field(
        column_name="State",
        attribute="state",
        default="",
        widget=widgets.CharWidget(allow_blank=True, coerce_to_string=True),
    )
    zip = Field(
        column_name="Zip",
        attribute="zip",
        default="",
        widget=custom_widgets.ZipWidget(),
    )
    phone = Field(
        column_name="Company Phone Number",
        attribute="phone",
        default="",
        widget=custom_widgets.PhoneNumberWidget(),
    )
    contact_first_name = Field(
        column_name="Contact First Name",
        default="",
        widget=widgets.CharWidget(allow_blank=True, coerce_to_string=True),
    )
    contact_last_name = Field(
        column_name="Contact Last Name",
        default="",
        widget=widgets.CharWidget(allow_blank=True, coerce_to_string=True),
    )
    contact_email = Field(
        column_name="Contact Email",
        default="",
        widget=widgets.CharWidget(allow_blank=True, coerce_to_string=True),
    )
    contact_work_phone = Field(
        column_name="Contact Work Phone",
        default="",
        widget=custom_widgets.PhoneNumberWidget(),
    )
    contact_mobile_phone = Field(
        column_name="Contact Mobile Phone",
        default="",
        widget=custom_widgets.PhoneNumberWidget(),
    )


class StoredMemberImportResource(CeleryResourceMixin, StoredMemberResource):
    """Import stored member data."""

    SUPPORTED_FORMATS = SUPPORTED_IMPORT_FORMATS

    def __init__(self, *args, **kwargs) -> None:
        self.chamber_id = kwargs.pop("chamber_id", None)
        super().__init__(*args, **kwargs)

    def init_instance(self, row=None) -> StoredMember:
        """Populate chamber data for new instances."""
        return self.Meta.model(chamber_id=self.chamber_id)

    def get_instance(self, instance_loader, row) -> StoredMember | None:
        """Search for member if exists."""
        try:
            name_field = self.fields["name"]
            name = name_field.clean(row)
            return self.get_queryset().get(
                name=name,
                chamber_id=self.chamber_id,
            )
        except self.Meta.model.DoesNotExist:
            return None

    class Meta:
        model = StoredMember
        fields = (
            "chamber_id",
            "name",
            "address",
            "city",
            "state",
            "zip",
            "phone",
            "contact_first_name",
            "contact_last_name",
            "contact_email",
            "contact_work_phone",
            "contact_mobile_phone",
        )
        required_fields = (
            "name",
            "address",
            "city",
            "state",
            "zip",
            "contact_first_name",
            "contact_last_name",
            "contact_email",
        )
        store_instance = True

    def skip_row(self, instance, original, row, import_validation_errors=None):
        """Skip empty rows.

        Excel files sometimes contain many empty rows, which causes errors
        during import because empty cells are treated as None.

        """
        if not any(row.values()):
            return True
        return super().skip_row(
            instance,
            original,
            row,
            import_validation_errors,
        )

    # pylint: disable=no-member
    def before_import_row(self, row, row_number=None, **kwargs):
        """Check if required fields don't have values.

        Only raise error if number of missing fields is different from number
        of row's fields, because if all fields are missing, it should be
        handled by `skip_row`.

        """
        # TODO: Find solution to skip empty rows in excel files
        missing_fields_count = 0
        missing_required_fields = []
        for field in self.get_fields():
            field_value = row[field.column_name]
            if field_value not in ("", None):
                continue
            missing_fields_count += 1
            if self.get_field_name(field) in self._meta.required_fields:
                missing_required_fields.append(field.column_name)
        if missing_fields_count == len(row):
            return
        if missing_required_fields:
            raise ValueError(
                f"Required fields: {', '.join(missing_required_fields)}",
            )

    # pylint: disable=too-many-arguments
    def import_row(
        self,
        row,
        instance_loader,
        using_transactions=True,
        dry_run=False,
        raise_errors=False,
        force_import=False,
        **kwargs,
    ):
        """Skip importing for empty rows.

        Need a custom here because the super `import_row` only calls the
        `skip_row` method if there is any error in the import progress.

        """
        if not any(row.values()):
            return RowResult()
        result = super().import_row(
            row,
            instance_loader,
            using_transactions,
            dry_run,
            raise_errors,
            force_import,
            **kwargs,
        )
        if result.validation_error:
            result.errors.append(result.validation_error)
        return result

    def after_import_row(self, row, row_result, row_number=None, **kwargs):
        """Add member's contact after importing it."""
        contact_email = self.fields["contact_email"].clean(row)
        if contact_email:
            contact_info = {
                "email": contact_email,
                "first_name": self.fields["contact_first_name"].clean(row),
                "last_name": self.fields["contact_last_name"].clean(row),
                "work_phone": self.fields["contact_work_phone"].clean(row),
                "mobile_phone": self.fields["contact_mobile_phone"].clean(row),
            }
            add_stored_member_contact(
                stored_member=row_result.instance,
                contact_info=contact_info,
            )
        return super().after_import_row(row, row_result, row_number, **kwargs)


class StoredMemberImportTemplateResource(StoredMemberResource):
    """Generate import template files."""

    def get_queryset(self):
        """Return examples data in template file."""
        return [
            StoredMember(
                id=1,
                name="Company Name Example 1",
                address="Example Last Name 1",
                city="City Example 1",
                state="AA",
                zip="111111",
                phone="1111111111",
            ),
            StoredMember(
                id=2,
                name="Company Name Example 2",
                address="Example Last Name 2",
                city="City Example 2",
                state="BB",
                zip="222222",
                phone="2222222222",
            ),
        ]

    def dehydrate_contact_first_name(self, instance: StoredMember):
        """Return example values."""
        return f"Contact First Name Example {instance.id}"

    def dehydrate_contact_last_name(self, instance: StoredMember):
        """Return example values."""
        return f"Contact Last Name Example {instance.id}"

    def dehydrate_contact_email(self, instance: StoredMember):
        """Return example values."""
        return f"example{instance.id}@mail.com"

    def dehydrate_contact_mobile_phone(self, instance: StoredMember):
        """Return example values."""
        return str(instance.id) * 11

    def dehydrate_contact_work_phone(self, instance: StoredMember):
        """Return example values."""
        return str(instance.id) * 11
