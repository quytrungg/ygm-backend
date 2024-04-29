from .health_check import HEALTH_CHECKS_APPS

# Application definition
INSTALLED_APPS = (
    "django.contrib.auth",
    "dal",
    "dal_select2",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
)

DRF_PACKAGES = (
    "rest_framework",
    "django_filters",
    "knox",
    "drf_spectacular",
    "drf_standardized_errors",
)

THIRD_PARTY = (
    "storages",
    "imagekit",
    "django_celery_beat",
    "django_extensions",
    "django_advanced_password_validation",
    "import_export",
    "import_export_extensions",
    "ordered_model",
    "ckeditor",
    "citext",
)

LOCAL_APPS = (
    "apps.core",
    "apps.users",
    "apps.resources",
    "apps.members",
    "apps.chambers",
    "apps.campaigns",
    "apps.timelines",
    "apps.incentives",
    "apps.historical_data",
)

INSTALLED_APPS += DRF_PACKAGES + THIRD_PARTY + HEALTH_CHECKS_APPS + LOCAL_APPS
