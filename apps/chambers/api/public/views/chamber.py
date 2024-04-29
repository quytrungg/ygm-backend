from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .. import serializers


class ChamberSubdomainValidateAPIView(GenericAPIView):
    """Viewset to validate subdomain in volunteer site."""

    serializer_class = serializers.ChamberSubdomainValidateSerializer
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        """Validate subdomain for volunteer site."""
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        if not serializer.data.get("chamber"):
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(data=serializer.data)
