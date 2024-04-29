# Installing project for developing on local PC

You have to have the following tools installed prior initializing the project:

- [docker](https://docs.docker.com/engine/installation/)
- [docker-compose](https://docs.docker.com/compose/install/)
- [pack-cli](https://buildpacks.io/docs/tools/pack/)
- [pyenv](https://github.com/pyenv/pyenv)
- [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)

## Backend

### Task runner

For easier running of everyday tasks, like:

* run dev server
* run all tests
* run linters
* run celery workers
* ...

We use [invoke](https://pypi.org/project/invoke/).

It provides shortcuts for most of the tasks, so it's like collection of bash scrips
or makefile or `npm scripts`.

To enable autocompletion of invoke commands add this line to your `~/.zshrc`

```
source <(inv --print-completion-script zsh)
```

### Python interpreter

Also `invoke` abstract "python interpreter", so you can use both `virtual env` and
`dockerized` python interpreter for working with project (see `.invoke` file).

* `virtualenv` is the default approach that requires python interpreter,
virtualenv, etc.
* `dockerized` is simpler for quick starting project and for experienced
developers

Suggested approach is using `virtualenv`

### Services

Project may use external services like Database (postgres), message broker,
cache (redis). For easier set up they are defined in `docker-compose.yml` file,
and they are automatically prepared / started when using `invoke`.

## Frontend

You can run frontend application for debugging or testing by simply using
`inv frontend.run`. This command clones frontend repository and puts it in the
parent dir, then installs node packages and runs application. Please, ensure you
have a compatible version of `node` installed
(install [nvm](https://github.com/nvm-sh/nvm) to manage node versions).

Current node version: **TODO: set current node version required for frontend app**

**Note**: You can change link/path to frontend app repository in
[provision/frontend.py](/provision/frontend.py).


# Prepare python env using virtualenv

1. Set up aliases for docker hosts in `/etc/hosts`:

```
127.0.0.1 postgres
127.0.0.1 redis
```

2. Create separate python virtual environment if you are going to run it in
local:

```bash
pyenv virtualenv-delete --force ygm-backend
pyenv install 3.11 --skip-existing
pyenv virtualenv `pyenv latest 3.11` ygm-backend
pyenv local ygm-backend
pyenv activate ygm-backend
```

3. Set up packages for using `invoke`

```bash
pip install -r requirements/local_build.txt
```

4. Start project initialization that will set up docker containers,
python/system env:

```bash
inv project.init
```
> [!IMPORTANT]
>
> This step might need installing additional dependencies for
> `mysqlclient`. Those might be OS specific. For Arch based `libmysqlclient`
> is enough.

5. Run the project and go to `localhost:8000` page in browser to check whether
it was started:

```bash
inv django.run
```

That's it. After these steps, the project will be successfully set up.

Once you run `project.init` initially you can start web server with
`inv django.run` command without executing `project.init` call.

# PyCharm console
Open Pycharm `settings`->`Build,Execution,Deployment`->`Console`->`Django Console` then
copy below into Starting script

```python
from django_extensions.management.shells import import_objects
from django.core.management.color import no_style

globals().update(
    import_objects({"dont_load": [], "quiet_load": False}, no_style())
)
```

# Devops tools
You will need:
* [kubectl](https://kubernetes.io/docs/tasks/tools/)
* [teleport](https://goteleport.com/docs/getting-started/)

Most of needed shortcuts can be called via invoke `inv k8s.###`. Just make sure that you log in with
`inv k8s.login`

```
k8s.logs
k8s.python-shell
```

# Historical Database

YGM Originally was developed using PHP and has historical database. If you need
access to the historical data you can connect to the MYSQL pod using following command.
```bash
POD=`kubectl get pods -n utils --selector=app=saritasa-rocks-mysql-port-forward -o jsonpath='{.items[*].metadata.name}'`
kubectl port-forward -n utils pod/$POD 3306:3306
```
