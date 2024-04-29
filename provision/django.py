from invoke import FailingResponder, Failure, Responder, task

from . import common, docker, start, system


def wait_for_database(context):
    """Ensure that database is up and ready to accept connections.

    Function called just once during subsequent calls of management commands.

    """
    if hasattr(wait_for_database, "_called"):
        return
    docker.up(context)
    start.run_python(
        context,
        " ".join(["manage.py", "wait_for_database", "--stable 0"]),
    )
    wait_for_database._called = True  # pylint: disable=protected-access


@task
def manage(context, command, watchers=()):
    """Run ``manage.py`` command.

    This command also handle starting of required services and waiting DB to
    be ready.

    Args:
        context: Invoke context
        command: Manage command
        watchers: Automated responders to command

    """
    wait_for_database(context)
    return start.run_python(
        context,
        " ".join(["manage.py", command]),
        watchers=watchers,
    )


@task
def makemigrations(context):
    """Run makemigrations command and chown created migrations."""
    common.success("Django: Make migrations")
    manage(context, "makemigrations")
    if not start.is_local_python:
        system.chown(context)


@task
def check_new_migrations(context):
    """Check if there is new migrations or not."""
    common.success("Checking migrations")
    manage(context, "makemigrations --check --dry-run")


@task
def migrate(context):
    """Run ``migrate`` command."""
    common.success("Django: Apply migrations")
    manage(context, "migrate")


@task
def resetdb(context, apply_migrations=True):
    """Reset database to initial state (including test DB)."""
    common.success("Reset database to its initial state")
    manage(context, "drop_test_database --noinput")
    manage(context, "reset_db -c --noinput")
    if not apply_migrations:
        return
    makemigrations(context)
    migrate(context)
    createsuperuser(context)
    set_default_site(context)


@task
def createsuperuser(
    context,
    email="root@root.com",
    username="root",
    password="root",
):
    """Create superuser."""
    common.success("Create superuser")
    responder_email = FailingResponder(
        pattern=r"Email address: ",
        response=email + "\n",
        sentinel="That Email address is already taken.",
    )
    responder_user_name = Responder(
        pattern=r"Username: ",
        response=username + "\n",
    )
    responder_password = Responder(
        pattern=r"(Password: )|(Password \(again\): )",
        response=password + "\n",
    )

    try:
        manage(
            context,
            command="createsuperuser",
            watchers=[
                responder_email,
                responder_user_name,
                responder_password,
            ],
        )
    except Failure:
        common.warn("Superuser with that email already exists. Skipped.")


@task
def run(context):
    """Run development web-server."""
    common.success("Running web app")
    if start.is_local_python:
        manage(context, "runserver_plus 0.0.0.0:8000")
    else:
        # not used `manage` as for `runserver` command need to pass
        # `--service-ports` argument which is not required for other
        # `manage` commands

        docker.docker_compose_run(
            context,
            params="--rm --service-ports",
            container="web",
            command="python3 manage.py runserver_plus 0.0.0.0:8000",
        )


@task
def shell(context, params=""):
    """Shortcut for manage.py shell_plus command.

    Additional params available here:
        https://django-extensions.readthedocs.io/en/latest/shell_plus.html

    """
    common.success("Entering Django Shell")
    manage(context, f"shell_plus --ipython {params}")


@task
def dbshell(context):
    """Open postgresql shell with credentials from either local or dev env."""
    common.success("Entering DB shell")
    manage(context, "dbshell")


def set_default_site(context):
    """Set default site to localhost.

    Set default site domain to `localhost:8000` so `get_absolute_url` works
    correctly in local environment

    """
    manage(
        context,
        "set_default_site --name localhost:8000 --domain localhost:8000",
    )


@task
def startapp(context):
    """Create new django app."""
    context.run(
        "cookiecutter "
        "git@github.com:saritasa-nest/saritasa-python-boilerplate-django.git "
        "--directory='app_template' --output-dir='apps'",
    )
