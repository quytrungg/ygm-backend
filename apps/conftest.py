from rest_framework import test

import pytest


@pytest.fixture
def api_client() -> test.APIClient:
    """Create api client."""
    return test.APIClient()
