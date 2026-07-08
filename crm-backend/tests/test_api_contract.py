def test_index_serves_frontend(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "CRM-MiniSystem" in response.text
    assert "Ответственный" in response.text
    assert "/static/app.js" in response.text


def test_leads_require_authentication(client) -> None:
    response = client.get("/api/v1/leads")

    assert response.status_code == 401


def test_openapi_contains_mvp_tags(client) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/leads" in paths
    assert "/api/v1/leads/export.csv" in paths
    assert "/api/v1/leads/import.csv" in paths
    assert "/api/v1/leads/{lead_id}/comments" in paths
    assert "/api/v1/dictionaries/statuses" in paths
    assert "/api/v1/reports/summary" in paths
