import sys
import decouple

import sentry_sdk

from .common import *

from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = decouple.config("DEBUG", default=False, cast=bool)

# Enable restriction to access debug tools like swagger, django debug toolbars,
# Admin page for non-local envs
RESTRICT_DEBUG_ACCESS = True
ENVIRONMENT = decouple.config("ENVIRONMENT")
FRONTEND_URL = decouple.config("FRONTEND_URL", default="")
# ------------------------------------------------------------------------------
# DATABASES - PostgreSQL
# ------------------------------------------------------------------------------
DATABASES["default"].update(
    NAME=decouple.config("RDS_DB_NAME"),
    USER=decouple.config("RDS_DB_USER"),
    PASSWORD=decouple.config("RDS_DB_PASSWORD"),
    HOST=decouple.config("RDS_DB_HOST"),
    PORT=decouple.config("RDS_DB_PORT"),
)
# ------------------------------------------------------------------------------
# AWS S3 - Django Storages S3
# ------------------------------------------------------------------------------
AWS_STORAGE_BUCKET_NAME = decouple.config("AWS_S3_BUCKET_NAME")
AWS_S3_REGION_NAME = decouple.config("AWS_S3_DIRECT_REGION")
AWS_S3_DIRECT_REGION = AWS_S3_REGION_NAME
AWS_S3_ENDPOINT_URL = f"https://s3.{AWS_S3_REGION_NAME}.amazonaws.com"
AWS_DEFAULT_ACL = "public-read"
# ------------------------------------------------------------------------------
# EMAIL SETTINGS
# ------------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = decouple.config("EMAIL_HOST")
EMAIL_HOST_USER = decouple.config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = decouple.config("EMAIL_HOST_PASSWORD")
EMAIL_PORT = decouple.config("EMAIL_HOST_PORT", cast=int)
EMAIL_USE_TLS = decouple.config("EMAIL_HOST_USE_TLS", cast=bool)
DEFAULT_FROM_EMAIL = (
    decouple.config("DEFAULT_FROM_EMAIL") or "no-reply@ygm-backend.com"
)
SERVER_EMAIL = decouple.config("SERVER_EMAIL", DEFAULT_FROM_EMAIL)

redis_host = decouple.config("REDIS_HOST")
redis_port = decouple.config("REDIS_PORT", cast=int)
redis_db = decouple.config("REDIS_DB", cast=int)
# ------------------------------------------------------------------------------
# CELERY
# ------------------------------------------------------------------------------
CELERY_TASK_DEFAULT_QUEUE = (
    f"{APP_LABEL.lower().replace(' ', '-')}-{ENVIRONMENT}"
)
CELERY_BROKER_URL = f"redis://{redis_host}:{redis_port}/{redis_db}"
CELERY_RESULT_BACKEND = f"redis://{redis_host}:{redis_port}/{redis_db}"

# ------------------------------------------------------------------------------
# REDIS
# ------------------------------------------------------------------------------
# Setting needed for redis health check
REDIS_URL = f"redis://{redis_host}:{redis_port}/{redis_db}"
CACHES["default"].update(
    LOCATION=REDIS_URL,
)
# ------------------------------------------------------------------------------
# DJANGO SECURITY
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# ------------------------------------------------------------------------------
SECRET_KEY = decouple.config("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = ["*"]
# disable django DEBUG if we run celery worker
if "celery" in sys.argv[0]:
    DEBUG = False
if DEBUG:
    # Dev tools settings
    from .common.dev_tools import *
# Start up sentry
sentry_sdk.init(
    dsn=decouple.config("SENTRY_DSN"),
    environment=ENVIRONMENT,
    **SENTRY_CONFIG,
)

# Old DB config
OLD_MYSQL_HOST = decouple.config("RDS_OLD_DB_HOST")
OLD_MYSQL_USER = decouple.config("RDS_OLD_DB_USER")
OLD_MYSQL_PASSWORD = decouple.config("RDS_OLD_DB_PASSWORD")
OLD_MYSQL_DATABASE = decouple.config("RDS_OLD_DB_NAME")

# Twilio SMS Info
TWILIO_PHONE_NUMBER = decouple.config("TWILIO_PHONE_NUMBER")
TWILIO_ACCOUNT_SID = decouple.config("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = decouple.config("TWILIO_AUTH_TOKEN")
