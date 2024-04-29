import socket
import sys

from .common import *

FRONTEND_URL = ""
ENVIRONMENT = "local"
DEBUG = True
RESTRICT_DEBUG_ACCESS = False

# Import dev tools only when DEBUG enable
if DEBUG:
    from .common.dev_tools import *

# disable django DEBUG if we run celery worker
if "celery" in sys.argv[0]:
    DEBUG = False

INTERNAL_IPS = (
    "0.0.0.0",
    "127.0.0.1",
)
# Hack to have working `debug` context processor when developing with docker
ip = socket.gethostbyname(socket.gethostname())
INTERNAL_IPS += (ip[:-1] + "1",)

DATABASES["default"].update(
    NAME="ygm-backend-dev",
    USER="ygm-backend-user",
    PASSWORD="manager",
    HOST="postgres",
    PORT="5432",
    CONN_MAX_AGE=0,
)

# Don't use celery when you're local
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_ROUTES = {}
CELERY_BROKER_URL = "redis://redis/1"
CELERY_RESULT_BACKEND = "redis://redis/1"
CELERY_TASK_DEFAULT_QUEUE = "development"

STORAGES["default"]["BACKEND"] = "django.core.files.storage.FileSystemStorage"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@ygm-backend.com"
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# disable any password restrictions
AUTH_PASSWORD_VALIDATORS = []

CACHES["default"].update(
    LOCATION="redis://redis/1",
)

MIDDLEWARE += (
    "corsheaders.middleware.CorsMiddleware",
)

INSTALLED_APPS += (
    'django_probes',  # wait for DB to be ready to accept connections
    "corsheaders",
)

# Provide CORS for local development
# This is necessary when developer wants to run the frontend application
# locally and communicate with the local backend server. This does not affect
# django applications with their own frontend or mobile APIs
# see doc here
# https://github.com/ottoyiu/django-cors-headers/
CORS_ORIGIN_ALLOW_ALL = True
# Custom headers
CORS_EXPOSE_HEADERS = ()
CORS_ALLOW_HEADERS = (
    "x-requested-with",
    "content-type",
    "accept",
    "origin",
    "authorization",
    "x-csrftoken",
    "user-agent",
    "accept-encoding",
    # Sentry headers
    "baggage",
    "sentry-trace",
    "chamber",
    "campaign",
)

# Old DB config
OLD_MYSQL_HOST = ""
OLD_MYSQL_USER = ""
OLD_MYSQL_PASSWORD = ""
OLD_MYSQL_DATABASE = ""

# Twilio SMS Info
TWILIO_PHONE_NUMBER = "+18666996047"
TWILIO_ACCOUNT_SID = "account_sid"
TWILIO_AUTH_TOKEN = "auth_token"
