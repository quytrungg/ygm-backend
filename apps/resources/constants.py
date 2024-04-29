from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class FileTypes(TextChoices):
    """Possible file types."""

    DOC = "doc", _("Document")
    PDF = "pdf", _("PDF")
    VIDEO = "video", _("Video")
    IMAGE = "image", _("Image")


DEFAULT_RESOURCE_CATEGORIES = [
    {
        "name": "MarComm",
    },
    {
        "name": "Sales Tools",
    },
    {
        "name": "Site Training",
    },
    {
        "name": "Sponsorship Examples",
    },
    {
        "name": "Trainings",
    },
    {
        "name": "TRC Events",
    },
    {
        "name": "TRC Management",
    },
    {
        "name": "Volunteer Engagement",
    },
]
