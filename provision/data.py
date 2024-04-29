import os

from invoke import task

from . import common, django, k8s

DB_DUMP_COMMAND = (
    "PGPASSWORD=${DB_PASSWORD} "
    "pg_dump "
    "--no-owner "
    "--dbname=${DB_NAME} "
    "--host=${DB_HOST} "
    "--port=${DB_PORT} "
    "--username=${DB_USER} "
    "--file ${DUMP_FILE}.sql"
)
REMOTE_DB_DUMP_COMMAND = (
    "pg_dump "
    "--no-owner "
    "--dbname={DB_NAME} "
    "--host={DB_HOST} "
    "--port={DB_PORT} "
    "--username={DB_USER} "
    "--file {DUMP_FILE}.sql"
)
DB_LOAD_COMMAND = (
    "PGPASSWORD=${DB_PASSWORD} "
    "psql "
    "--quiet "
    "--dbname=${DB_NAME} "
    "--host=${DB_HOST} "
    "--port=${DB_PORT} "
    "--username=${DB_USER} "
    "--file ${DUMP_FILE}.sql"
)


@task
def fill_sample_data(context):
    """Prepare sample data for local usage."""
    raise NotImplementedError("Implement sample data generation")


@task
def load_db_dump(context, file="local_db_dump"):
    """Load db dump to local db."""
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.local"
    common.success("Resetting local db")
    django.resetdb(context, apply_migrations=False)
    db_config = _get_local_db_config()
    db_config.update(DUMP_FILE=file)
    context.run(DB_LOAD_COMMAND, env=db_config)
    common.success("DB is ready for use")


@task
def backup_local_db(context):
    """Back up local db."""
    common.success("Creating backup of local db.")
    db_config = _get_local_db_config()
    db_config.update(DUMP_FILE="local_db_dump")
    context.run(command=DB_DUMP_COMMAND, env=db_config)


@task
def backup_remote_db(context):
    """Create and get remote db dump."""
    common.success("Creating backup of remote db.")
    db_config = _get_remote_db_config(context)
    db_config.update(DUMP_FILE=f"/tmp/{k8s.NAMESPACE}_db_dump")
    command = REMOTE_DB_DUMP_COMMAND.format(**db_config)
    k8s.postgres_create_dump(
        context,
        command=command,
        password=db_config["DB_PASSWORD"],
    )
    k8s.postgres_get_dump(context)


def _get_local_db_config() -> dict:
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.local"
    from django.conf import settings

    db_settings = settings.DATABASES["default"]
    return {
        "DB_HOST": db_settings["HOST"],
        "DB_NAME": db_settings["NAME"],
        "DB_PASSWORD": db_settings["PASSWORD"],
        "DB_PORT": str(db_settings["PORT"]),
        "DB_USER": db_settings["USER"],
    }


def _get_remote_db_config(context) -> dict:
    # python-decouple is installed with inv project.build
    # so we import decouple this way because it may not be installed
    # at the project initialization stage
    import decouple

    env_data = k8s.get_remote_file(
        context,
        path_to_file="/workspace/app/config/settings/.env",
    )
    env_path = "config/settings/.env.tmp"

    with open(env_path, "w", encoding="UTF-8") as file:
        file.write(env_data)

    env_config = decouple.Config(decouple.RepositoryEnv(env_path))
    settings = {
        "DB_NAME": env_config("RDS_DB_NAME"),
        "DB_USER": env_config("RDS_DB_USER"),
        "DB_PASSWORD": env_config("RDS_DB_PASSWORD"),
        "DB_HOST": env_config("RDS_DB_HOST"),
        "DB_PORT": env_config("RDS_DB_PORT"),
    }
    context.run(f"rm {env_path}")
    return settings
