from config.celery import app

from .models import DataImportJob


@app.task(
    track_started=True,
)
def import_historical_data(job_id):
    """Call import data on data import job instance."""
    DataImportJob.objects.get(id=job_id).import_data()
