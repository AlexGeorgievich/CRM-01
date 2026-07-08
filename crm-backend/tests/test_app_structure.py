from app.main import app
from app.models import Base


def test_core_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/" in paths
    assert "/health" in paths
    assert "/api/v1/ping" in paths
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/auth/me" in paths
    assert "/api/v1/leads" in paths
    assert "/api/v1/users" in paths
    assert "/api/v1/dictionaries/statuses" in paths


def test_domain_tables_are_registered() -> None:
    assert {
        "users",
        "leads",
        "comments",
        "statuses",
        "courses",
        "sources",
    }.issubset(Base.metadata.tables.keys())
