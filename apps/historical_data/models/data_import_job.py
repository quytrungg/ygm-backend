import traceback
import uuid

from django.conf import settings
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.historical_data.services.importer import import_all_chamber_data


# pylint: disable=attribute-defined-outside-init,broad-exception-caught
class DataImportJob(BaseModel):
    """Store information on old data import job."""

    class ImportStatus(models.TextChoices):
        """ImportJob possible statuses.

        * CREATED:
            import job is just created
        * IMPORT_CONFIRMED
            import confirmed but not started yet
        * IMPORTING:
            importing job started
        * IMPORTED:
            data imported to DB w/o errors
        * IMPORT_ERROR:
            unknown error during import

        State diagrams::
            .save()
               |
            CREATED
               |
            IMPORT_CONFIRMED
               |
            .import_data()
               |
            IMPORTING - IMPORT_ERROR
               |
            IMPORTED

        """

        CREATED = "CREATED", _("Created")
        CONFIRMED = "CONFIRMED", _("Import confirmed")
        IMPORTING = "IMPORTING", _("Importing")
        IMPORTED = "IMPORTED", _("Imported")
        IMPORT_ERROR = "IMPORT_ERROR", _("Import error")

    job_kwargs = models.JSONField(
        default=dict,
        verbose_name=_("Job kwargs"),
        help_text=_(
            "Keyword parameters required for job initialization. "
            "Should look like {\"chamber_ids\": [546]}",
        ),
    )
    traceback = models.TextField(
        blank=True,
        default=str,
        verbose_name=_("Traceback"),
        help_text=_("Python traceback in case of import error"),
    )
    error_message = models.CharField(
        max_length=128,
        blank=True,
        default=str,
        verbose_name=_("Error message"),
        help_text=_("Python error message in case of import error"),
    )
    status = models.CharField(
        max_length=20,
        choices=ImportStatus.choices,
        default=ImportStatus.CREATED,
        verbose_name=_("Job Status"),
    )
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        editable=False,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Created by"),
        help_text=_("User which started job"),
    )
    target_chamber = models.ForeignKey(
        to="chambers.Chamber",
        verbose_name=_("Target Chamber"),
        help_text=_("Chamber which data are imported into"),
        null=True,
        on_delete=models.SET_NULL,
    )
    result = models.JSONField(
        default=dict,
        verbose_name=_("Job result"),
        help_text=_(
            "Number of imported objects per instance.",
        ),
    )
    task_id = models.CharField(
        max_length=36,
        default=str,
        verbose_name=_("Task ID"),
        help_text=_("Celery task ID that start importing"),
    )

    class Meta:
        verbose_name = _("Import Job")
        verbose_name_plural = _("Import Jobs")

    def save(self, *args, **kwargs):
        """Trigger import execution."""
        is_created = self._state.adding
        super().save(*args, **kwargs)
        if not is_created:
            return
        self.task_id = str(uuid.uuid4())
        self.save(update_fields=["task_id"])
        transaction.on_commit(self._start_import)

    def _start_import(self):
        """Start async celery task."""
        from ..tasks import import_historical_data
        self.status = self.ImportStatus.CONFIRMED
        self.save(update_fields=["status"])
        import_historical_data.apply_async(
            kwargs={"job_id": self.pk},
            task_id=self.task_id,
        )

    def import_data(self):
        """Import data base on kwargs."""
        chamber_ids = self.job_kwargs.get("chamber_ids", [])
        self.status = self.ImportStatus.IMPORTING
        self.save(update_fields=["status"])
        if not chamber_ids:
            self.status = self.ImportStatus.IMPORTED
            self.save(update_fields=["status"])
            return

        try:
            with transaction.atomic():
                self.result = import_all_chamber_data(
                    chamber_ids,
                    target_chamber_id=self.target_chamber_id,
                )
                self.status = self.ImportStatus.IMPORTED
                self.save(
                    update_fields=[
                        "result",
                        "status",
                    ],
                )
        except Exception as error:
            self.traceback = traceback.format_exc()
            self.error_message = str(error)[:128]
            self.status = self.ImportStatus.IMPORT_ERROR
            self.save(
                update_fields=[
                    "traceback",
                    "error_message",
                    "status",
                ],
            )
