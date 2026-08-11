from fastapi.testclient import TestClient
from app.core.config import settings


def test_health_endpoint(client: TestClient):
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["project"] == settings.PROJECT_NAME
    assert data["version"] == settings.VERSION
