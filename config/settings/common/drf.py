# Rest framework API configuration
from datetime import timedelta

from libs.utils import get_latest_version

# https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "apps.core.api.auth.TokenAuthentication",
        # SessionAuthentication is also used for CSRF
        # validation on ajax calls from the frontend
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "libs.api.renderers.CustomBrowsableAPIRenderer",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_standardized_errors.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": (
        "libs.api.filter_backends.CustomDjangoFilterBackend",
        "libs.open_api.filters.OrderingFilterBackend",
        "libs.open_api.filters.SearchFilterBackend",
    ),
    "DEFAULT_PAGINATION_CLASS": (
        "libs.api.pagination.CustomLimitOffsetPagination"
    ),
    "PAGE_SIZE": 25,
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# Limit max objects in list APIs
MAX_PAGINATION_SIZE = 1000

# https://drf-spectacular.readthedocs.io/en/latest/settings.html
SPECTACULAR_SETTINGS = {
    "TITLE": "ygm Api",
    "DESCRIPTION": "Api for ygm",
    "VERSION": get_latest_version("CHANGELOG.md"),
    "POSTPROCESSING_HOOKS": [
        "drf_standardized_errors.openapi_hooks.postprocess_schema_enums",
    ],
    "ENUM_NAME_OVERRIDES": {
        "ValidationErrorEnum": "drf_standardized_errors.openapi_serializers.ValidationErrorEnum.values",
        "ClientErrorEnum": "drf_standardized_errors.openapi_serializers.ClientErrorEnum.values",
        "ServerErrorEnum": "drf_standardized_errors.openapi_serializers.ServerErrorEnum.values",
        "ErrorCode401Enum": "drf_standardized_errors.openapi_serializers.ErrorCode401Enum.values",
        "ErrorCode403Enum": "drf_standardized_errors.openapi_serializers.ErrorCode403Enum.values",
        "ErrorCode404Enum": "drf_standardized_errors.openapi_serializers.ErrorCode404Enum.values",
        "ErrorCode405Enum": "drf_standardized_errors.openapi_serializers.ErrorCode405Enum.values",
        "ErrorCode406Enum": "drf_standardized_errors.openapi_serializers.ErrorCode406Enum.values",
        "ErrorCode415Enum": "drf_standardized_errors.openapi_serializers.ErrorCode415Enum.values",
        "ErrorCode429Enum": "drf_standardized_errors.openapi_serializers.ErrorCode429Enum.values",
        "ErrorCode500Enum": "drf_standardized_errors.openapi_serializers.ErrorCode500Enum.values",
        "TimelineStatus": "apps.timelines.constants.TimelineStatus",
        "CampaignStatus": "apps.campaigns.constants.CampaignStatus",
        "UserRole": "apps.users.constants.UserRole",
        "UserCampaignRoles": "apps.campaigns.constants.UserCampaignRole",
        "IncentiveType": "apps.incentives.constants.IncentiveType",
        "IncentiveQualifierName": "apps.incentives.constants.IncentiveQualifierName",
        "IncentiveQualifierAmount": "apps.incentives.constants.IncentiveQualifierAmount",
        "ContractStatus": "apps.members.constants.ContractStatus",
        "ContractType": "apps.members.constants.ContractType",
    },
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVE_PERMISSIONS": (
        "libs.permissions.HasAccessToDebugTools",
    ),
    "SWAGGER_UI_DIST": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.7",
}

# https://james1345.github.io/django-rest-knox/settings/
REST_KNOX = {
    "SECURE_HASH_ALGORITHM": "cryptography.hazmat.primitives.hashes.SHA512",
    "AUTH_TOKEN_CHARACTER_LENGTH": 64,
    "TOKEN_TTL": timedelta(weeks=2),
    "TOKEN_LIMIT_PER_USER": None,
    "AUTO_REFRESH": False,
    "USER_SERIALIZER": "apps.users.api.serializers.UserSerializer",
}
