# ------------------------------------------------------------------------------
# DATABASES - PostgreSQL
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
# ------------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "ATOMIC_REQUESTS": True,
        "CONN_MAX_AGE": 600,
    },
}

SAFE_DELETE_FIELD_NAME = "deleted_at"
