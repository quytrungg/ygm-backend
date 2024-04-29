from invoke import task

from . import docker, is_local_python


@task
def run(context):
    """Start celery worker."""
    if is_local_python:
        context.run(
            "celery --app config.celery:app "
            "worker --beat --scheduler=django --loglevel=info",
        )
    else:
        docker.up_containers(context, ["celery"])
