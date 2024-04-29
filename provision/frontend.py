import pathlib

import invoke

from . import common

FRONTEND_REPO_NAME = "ygm-frontend"
FRONTEND_REPO_PATH = pathlib.Path(f"../{FRONTEND_REPO_NAME}")
FRONTEND_REPO_LINK = f"git@github.com:saritasa-nest/{FRONTEND_REPO_NAME}.git"


# pylint: disable=too-many-arguments
@invoke.task
def run(
    context,
    frontend_repo_path: pathlib.Path = FRONTEND_REPO_PATH,
    backend_port: int = 8000,
    rebuild: bool = True,
    clean_build: bool = True,
    branch: str = "develop",
):
    """Run frontend locally.

    Params:
    - `--no-rebuild` param to just run `npm start` without reinstalling
    dependencies;
    - `--no-clean-build` to use `npm install` instead of `npm
    ci` during installing node packages;

    """
    if rebuild:
        common.success("Preparing frontend directory...")
        clone_repo(context, FRONTEND_REPO_LINK, frontend_repo_path, branch)
        install_dependencies(context, frontend_repo_path, clean_build)
        create_env_file(frontend_repo_path, backend_port)

    npm(context, command="start", frontend_repo_path=frontend_repo_path)


def clone_repo(
    context: invoke.Context,
    frontend_repo_link: str,
    frontend_repo_path: pathlib.Path,
    branch: str,
):
    """Clone repository with frontend."""
    if not frontend_repo_path.exists():
        common.success("Cloning frontend repository...")
        context.run(f"git clone {frontend_repo_link} {frontend_repo_path}")
        with context.cd(frontend_repo_path):
            context.run(f"git checkout {branch}")
        common.success(f"Successfully cloned to '{FRONTEND_REPO_PATH}'!")
    else:
        common.success("Pulling changes...")
        with context.cd(frontend_repo_path):
            context.run("git pull")
            context.run(f"git checkout {branch}")


def install_dependencies(
    context: invoke.Context,
    frontend_repo_path: pathlib.Path,
    clean_build: bool,
):
    """Install frontend dependencies via `npm ci`.

    `clean_build` param allows to choose strategy of updating dependencies. If
    True use `npm ci` otherwise use `npm install`

    """
    common.success("Installing frontend dependencies...")
    command = "ci" if clean_build else "install"
    npm(context, command=command, frontend_repo_path=frontend_repo_path)


def create_env_file(frontend_repo_path: pathlib.Path, backend_port: int):
    """Set up .env file for frontend.

    Set both `NG_APP_API_URL` and `REACT_APP_API_URL` to work with both the
    Angular/React framework in different projects. `VITE_API_URL` is required
    for React projects.

    """
    common.success("Creating env file...")
    env_file = pathlib.Path(frontend_repo_path) / ".env.development.local"
    possible_framework_prefixes = ("NG_APP", "REACT_APP", "VITE")
    backend_api_url_env_vars = "\n".join(
        f"{prefix}_API_URL='http://localhost:{backend_port}/api/v1/'"
        for prefix in possible_framework_prefixes
    )
    env_file.write_text(
        f"{backend_api_url_env_vars}\n",
        # Here you can add other settings for local frontend
    )


def npm(
    context: invoke.Context,
    command: str,
    frontend_repo_path: pathlib.Path,
):
    """Call `npm` inside frontend dir with passed command."""
    with context.cd(frontend_repo_path):
        context.run(f"npm {command}")
