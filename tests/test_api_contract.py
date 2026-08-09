import importlib.util
import os

import pytest

os.environ["MYTHARA_DATABASE_URL"] = "sqlite:///./knowledge/encyclopedia/api_test.db"

pytestmark = pytest.mark.skipif(
    not all(importlib.util.find_spec(m) for m in ("fastapi", "sqlalchemy", "pydantic")),
    reason="FastAPI/SQLAlchemy/Pydantic stack is not installed in this execution environment",
)


def test_required_api_endpoints_are_registered():
    from backend.app.main import app

    routes = {route.path for route in app.routes}
    assert "/api/ask" in routes
    assert "/api/suggest" in routes
    assert "/api/create/mythral" in routes
    assert "/api/approve" in routes
    assert "/api/mythral/{mythral_id}" in routes
    assert "/api/encyclopedia/search" in routes
