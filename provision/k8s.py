import os

from invoke import Responder, task

from . import common

NAMESPACE = "ygm"

POSTGRES_NAMESPACE = "utils"
POSTGRES_POD = (
    f"kubectl get pods --namespace {POSTGRES_NAMESPACE} "
    "--selector=app=saritasa-rocks-psql "
    "--output jsonpath='{.items[*].metadata.name}'"
)
POSTGRES_POD_EXEC = (
    f"kubectl exec -ti -n {POSTGRES_NAMESPACE} $({POSTGRES_POD})"
)


def _get_pod_cmd(component: str) -> str:
    """Get command for getting exact pod."""
    return (
        f"kubectl get pods "
        f"-n {NAMESPACE} "
        f"-l app.kubernetes.io/component={component} "
        f"--no-headers --output=\"custom-columns=NAME:.metadata.name\""
    )


@task
def login(context):
    """Login into k8s via teleport."""
    common.success("Login into kubernetes CI")
    context.run("tsh login --proxy=teleport.saritasa.rocks:443 --auth=github")


@task
def set_context(context):
    """Set k8s context to current project."""
    common.success("Setting context for k8s")
    context.run(
        f"kubectl config set-context --current --namespace={NAMESPACE}",
    )


@task(pre=[set_context])
def logs(context, component="backend"):
    """Get logs for k8s pod."""
    common.success(f"Getting logs from {component}")
    context.run(f"kubectl logs $({_get_pod_cmd(component)})")


@task(pre=[set_context])
def pods(context):
    """Get pods from k8s."""
    common.success("Getting pods")
    context.run("kubectl get pods")


@task(pre=[set_context])
def execute(
    context,
    entry="/cnb/lifecycle/launcher bash",
    component="backend",
    pty=None,
    hide=None,
):
    """Execute command inside k8s pod."""
    common.success(f"Entering into {component} with {entry}")
    return context.run(
        f"kubectl exec "
        f"-n {NAMESPACE} "
        f"-ti $({_get_pod_cmd(component)}) -- {entry}",
        pty=pty,
        hide=hide,
    )


@task
def python_shell(context, component="backend"):
    """Enter into python shell."""
    execute(context, component=component, entry="shell_plus")


@task
def health_check(context, component="backend"):
    """Check health of component."""
    execute(context, component=component, entry="health_check")


@task
def get_remote_file(
    context,
    component="backend",
    path_to_file="/workspace/app/config/settings/config.py",
):
    """Get config from pod."""
    return execute(
        context,
        component=component,
        entry=f"cat {path_to_file}",
        pty=False,
        hide="out",
    ).stdout


@task
def postgres_create_dump(
    context,
    command,
    password,
):
    """Execute command in postgres pod."""
    common.success(f"Entering into postgres with {command}")
    context.run(
        f"{POSTGRES_POD_EXEC} -- {command}",
        watchers=[
            Responder(
                pattern="Password: ",
                response=f"{password}\n",
            ),
        ],
    )


@task
def postgres_get_dump(
    context,
    file_name=f"{NAMESPACE}_db_dump.sql",
):
    """Download db data from postgres pod if it present."""
    common.success(f"Downloading dump({file_name}) from pod")
    current_folder = os.getcwd()
    context.run(
        f"kubectl cp --namespace {POSTGRES_NAMESPACE} "
        f"$({POSTGRES_POD}):tmp/{file_name} {current_folder}/{file_name}",
    )
    common.success(f"Downloaded dump({file_name}) from pod. Clean up")
    rm_command = f"rm tmp/{file_name}"
    context.run(
        f"{POSTGRES_POD_EXEC} -- {rm_command}",
    )
