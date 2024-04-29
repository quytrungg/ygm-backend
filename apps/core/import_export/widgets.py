import re

from import_export.widgets import CharWidget

from ..services import normalize_phone_number

ZIPCODE_PATTERN = re.compile(
    r"^\d{5}((-\d{1,4})|(\.0))?$",
)


class ZipWidget(CharWidget):
    """Handle logic to render/clean value for zipcode."""

    def __init__(self):
        super().__init__(coerce_to_string=True, allow_blank=True)

    def clean(self, value, row=None, **kwargs):
        """Return the zipcode."""
        cleaned_value = super().clean(value, row, **kwargs)
        if not cleaned_value:
            return cleaned_value
        match = ZIPCODE_PATTERN.match(cleaned_value)
        if not match:
            raise ValueError("Invalid zipcode")
        val = match.string.split(".")[0]
        return val


class PhoneNumberWidget(CharWidget):
    """Handle logic to render/clean value for phone numbers."""

    def __init__(self):
        super().__init__(coerce_to_string=True, allow_blank=True)

    def clean(self, value, row=None, **kwargs):
        """Return the normalized phone number."""
        cleaned_value = super().clean(value, row, **kwargs)
        return normalize_phone_number(cleaned_value)
