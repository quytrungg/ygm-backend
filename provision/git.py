import invoke

from . import common


@invoke.task
def setup(context):
    """Set up git for working."""
    pre_commit(context)
    # https://wiki.saritasa.rocks/general/git/#fast-forward-merges
    context.run("git config --add merge.ff false")
    # https://wiki.saritasa.rocks/general/git/#auto-merged-pulls
    context.run("git config --add pull.ff only")


@invoke.task
def pre_commit(context):
    """Install git hooks via pre-commit."""
    common.success("Setting up pre-commit")
    hooks = " ".join(
        f"--hook-type {hook}" for hook in (
            "pre-commit",
            "pre-push",
            "commit-msg",
        )
    )
    context.run(f"pre-commit install {hooks}")


@invoke.task
def run_hooks(context):
    """Install git hooks."""
    common.success("Running git hooks")
    context.run("pre-commit run --hook-stage push --all-files")


@invoke.task
def check_for_cruft_files(context):
    """Check that there is no cruft files."""
    found_files = context.run(
        "find  . -name '*.rej'",
        pty=False,
        hide="out",
    ).stdout
    if found_files:
        raise invoke.Exit(
            code=1,
            message=(
                "You have `.rej` files present, "
                "please resolve conflicts with cruft!"
            ),
        )
