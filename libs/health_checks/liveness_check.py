from django.db import transaction
from django.http import HttpResponse


@transaction.non_atomic_requests
def liveness_check(
    request,  # pylint: disable=unused-argument
) -> HttpResponse:
    """Check if app is alive.

    We disable atomic requests, because if you have ATOMIC_REQUEST=True django
    would still go to db to check the state, meaning there would an error
    when db is not available.

    Note: this endpoint is still dependant on db, if you logged in via browser,
    or in other words have session cookies.

    """
    return HttpResponse(status=204)
