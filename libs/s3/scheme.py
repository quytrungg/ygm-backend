from drf_spectacular.utils import extend_schema, extend_schema_view
from s3direct.api.serializers import S3DirectSerializer, S3UploadSerializer
from s3direct.api.views import S3DirectWrapper

extend_schema_view(
    post=extend_schema(
        request=S3DirectSerializer,
        responses=S3UploadSerializer,
    ),
)(S3DirectWrapper)
