from . import docker, is_local_python


def run_web(context, command, watchers=()):
    """Run command in``web`` container.

    docker-compose run --rm web <command>

    """
    return docker.docker_compose_run(
        context,
        params="--rm",
        container="web",
        command=command,
        watchers=watchers,
    )


def run_web_python(context, command, watchers=()):
    """Run command using web python interpreter."""
    return run_web(context, " ".join(["python3", command]), watchers=watchers)


def run_local_python(context, command: str, watchers=()):
    """Run command using local python interpreter."""
    return context.run(
        " ".join(["python3", command]),
        watchers=watchers,
    )


if is_local_python:
    run_python = run_local_python
else:
    run_python = run_web_python
