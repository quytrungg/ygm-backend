# https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-CACHES

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "MAX_ENTRIES": 1000,
        },
        "KEY_PREFIX": "ygm",
    },
}
