from typing import TYPE_CHECKING
from urllib.parse import ParseResult, urlparse

from django.conf import settings

if TYPE_CHECKING:
    from apps.chambers.models import Chamber


def get_chamber_url(chamber: "Chamber") -> str:
    """Return chamber's url from base url and its subdomain."""
    base_url = settings.FRONTEND_URL
    base_url_parsed = urlparse(base_url)
    return ParseResult(
        scheme=base_url_parsed.scheme,
        netloc=f"{chamber.subdomain}.{base_url_parsed.netloc}",
        path=base_url_parsed.path,
        params=base_url_parsed.params,
        query=base_url_parsed.query,
        fragment=base_url_parsed.fragment,
    ).geturl()
