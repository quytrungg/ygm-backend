from invoke import UnexpectedExit, task

from . import common

MAIN_CONTAINERS = [
    "postgres",
    "redis",
]


def docker_compose_run(
    context, params: str, container: str, command: str, watchers=(),
):
    """Run ``command`` using docker-compose.

    docker compose run <params> <container> <command>
    Start container and run command in it.

    Used function so lately it can be extended to use different docker-compose
    files.

    Args:
        context: Invoke context
        params: Configuration params for docker compose
        container: Name of container to start
        command: Command to run in started container
        watchers: Automated responders to command

    """
    cmd = f"docker compose run {params} {container} {command}"
    return context.run(cmd, watchers=watchers)


@task
def build(
    context,
    env="development",
    builder="public.ecr.aws/saritasa/buildpacks/google/builder:latest",
    runner="public.ecr.aws/saritasa/buildpacks/google/runner:latest",
    tag="ygm-backend",
):
    """Build app image using buildpacks.

    Actual versions may be found here:
        https://github.com/saritasa-nest/saritasa-devops-docker-images/tree/main/buildpacks/google/builder

    """
    # Builder needs requirements.txt
    context.run(f"cp requirements/{env}.txt requirements.txt")
    context.run(f"pack build --builder={builder} --run-image={runner} {tag}")
    context.run("rm requirements.txt")


def docker_compose_exec(context, service: str, command: str):
    """Run ``exec`` using docker-compose.

    docker compose exec <service> <command>
    Run commands in already running container.

    Used function so lately it can be extended to use different docker-compose
    files.

    Args:
        context: Invoke context
        service: Name of service to run command in
        command: Command to run in service container

    """
    cmd = f"docker compose exec {service} {command}"
    return context.run(cmd)


def stop_all_containers(context):
    """Shortcut for stopping ALL running docker containers."""
    context.run("docker stop $(docker ps -q)")


def up_containers(
    context,
    containers: tuple[str],
    detach=True,
    stop_others=True,
    **kwargs,
):
    """Bring up containers and run them.

    Add `d` kwarg to run them in background.

    Args:
        context: Invoke context
        containers: Name of containers to start
        detach: To run them in background
        stop_others: Stop ALL other containers in case of errors during `up`.
            Usually this happens when containers from other project uses the
            same ports, for example, Postgres and redis.

    Raises:
        UnexpectedExit: when `up` command wasn't successful

    """
    if containers:
        common.success(f"Bring up {', '.join(containers)} containers")
    else:
        common.success("Bring up all containers")
    up_cmd = (
        f"docker compose up "
        f"{'-d ' if detach else ''}"
        f"{' '.join(containers)}"
    )
    try:
        context.run(up_cmd)
    except UnexpectedExit as exception:
        if not stop_others:
            raise exception
        stop_all_containers(context)
        context.run(up_cmd)


def stop_containers(context, containers):
    """Stop containers."""
    common.success(f"Stopping {' '.join(containers)} containers ")
    cmd = f"docker compose stop {' '.join(containers)}"
    context.run(cmd)


# pylint: disable=invalid-name
@task
def up(context):
    """Bring up main containers and start them."""
    up_containers(
        context,
        containers=MAIN_CONTAINERS,
        detach=True,
    )


@task
def stop(context):
    """Stop main containers."""
    stop_containers(
        context,
        containers=MAIN_CONTAINERS,
    )


@task
def clear(context):
    """Stop and remove all containers defined in docker-compose.

    Also remove images.

    """
    common.success("Clearing docker-compose")
    context.run("docker compose rm -f")
    context.run("docker compose down -v --rmi all --remove-orphans")
