from import_export.formats import base_formats
from tablib.core import Dataset


class XLSX(base_formats.XLSX):
    """Custom XLSX format."""

    def create_dataset(self, in_stream):
        """Use the provided logic from tablib to avoid errors.

        See https://github.com/jazzband/tablib/issues/561

        Might revert to use import_export's class if it's fixed in v4.

        """
        return Dataset().load(in_stream=in_stream, format=self.get_extension())
