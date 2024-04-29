from functools import partial

from invoke import Exit, UnexpectedExit, task

from . import common, is_local_python, start

DEFAULT_FOLDERS = "apps libs provision conftest.py tasks.py"


@task
def pylint(context, path=DEFAULT_FOLDERS):
    """Run `pylint` linter."""
    common.success("Linters: PyLint running")
    execute = context.run if is_local_python else partial(
        start.run_web, context=context,
    )
    # path to settings module set as env variable instead of `.pylintrc`
    # because of incompatibility with celery (that set up settings during
    # import of celery app in `config/__init__.py`)
    context["run"].env["DJANGO_SETTINGS_MODULE"] = "config.settings.local"
    return execute(command=f"pylint {path}")


# pylint: disable=redefined-builtin
@task
def all(context, path=DEFAULT_FOLDERS):
    """Run all linters."""
    common.success("Linters: running all linters")
    linters = (pylint,)
    failed = []
    for linter in linters:
        try:
            linter(context, path)
        except UnexpectedExit:
            failed.append(linter.__name__)
    if failed:
        common.error(
            f"Linters failed: {', '.join(map(str.capitalize, failed))}",
        )
        raise Exit(code=1)
