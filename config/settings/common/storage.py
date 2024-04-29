from libs.s3.object_key_prefix import S3UUIDPrefixKey
from .paths import BASE_DIR


# Django Storages
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

AWS_S3_SECURE_URLS = False
AWS_QUERYSTRING_AUTH = False

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"
STATIC_ROOT = BASE_DIR / "static"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

S3DIRECT_URL_STRUCTURE = "https://{1}.{0}"      # {bucket}.{endpoint}
S3DIRECT_IMAGES_MIME_TYPES = (
    "image/jpeg",
    "image/png",
)
S3DIRECT_DOCUMENT_MIME_TYPES = (
    "application/pdf",
    # Doc
    "application/msword",
    # Docx
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
)
S3DIRECT_VIDEO_MIME_TYPES = (
    "video/mp4",
    "video/quicktime",
)
S3DIRECT_DESTINATIONS = dict(
    profile_images=dict(
        key=S3UUIDPrefixKey("profile_image"),
        allowed=S3DIRECT_IMAGES_MIME_TYPES,
    ),
    chamber_brandings=dict(
        key=S3UUIDPrefixKey("chamber_branding"),
        allowed=S3DIRECT_IMAGES_MIME_TYPES,
    ),
    resources=dict(
        key=S3UUIDPrefixKey("resource"),
        allowed=S3DIRECT_DOCUMENT_MIME_TYPES + S3DIRECT_VIDEO_MIME_TYPES,
    ),
    timelines=dict(
        key=S3UUIDPrefixKey("timeline"),
        allowed=S3DIRECT_DOCUMENT_MIME_TYPES + S3DIRECT_VIDEO_MIME_TYPES,
    ),
    products=dict(
        key=S3UUIDPrefixKey("product"),
        allowed=S3DIRECT_IMAGES_MIME_TYPES + S3DIRECT_VIDEO_MIME_TYPES,
    ),
)
DEFAULT_DESTINATION = "profile_images"
