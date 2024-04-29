from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.api.views import ChamberBaseViewSet


class ImpersonateTestViewSet(ChamberBaseViewSet):
    """Support impersonation method testing."""

    @action(methods=("get",), detail=False, url_name="info")
    def impersonation_info(self, request, *args, **kwargs):
        """Return info of `request.user` and `request.auth.user`.

        This viewset is used in test cases of impersonation.

        """
        return Response(
            data={
                "user_id": request.user.id,
                "auth_user_id": request.auth.user_id,
            },
        )
