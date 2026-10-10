from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """Test GET /api/v1/health returns 200, healthy status, and database connectivity."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["database_connected"] is True
    assert "environment" in data
    assert "version" in data
    assert "timestamp" in data


def test_root_endpoint(client: TestClient):
    """Test GET / returns project metadata and documentation paths."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Health Insurance Intelligence Platform"
    assert data["docs"] == "/docs"
    assert data["api_v1"] == "/api/v1"
