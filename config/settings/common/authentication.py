# Custom model for Auth
AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
)


# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        'NAME': 'django_advanced_password_validation.advanced_password_validation.ContainsDigitsValidator',
        'OPTIONS': {
            'min_digits': 1,
        },
    },
    {
        'NAME': 'django_advanced_password_validation.advanced_password_validation.ContainsUppercaseValidator',
        'OPTIONS': {
            'min_uppercase': 1,
        },
    },
    {
        'NAME': 'django_advanced_password_validation.advanced_password_validation.ContainsLowercaseValidator',
        'OPTIONS': {
            'min_lowercase': 1,
        },
    },
    {
        'NAME': 'django_advanced_password_validation.advanced_password_validation.ContainsSpecialCharactersValidator',
        'OPTIONS': {
            'min_characters': 1,
        },
    },
]
