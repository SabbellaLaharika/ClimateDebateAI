from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_policy_usa():
    response = client.get("/policies/usa")
    assert response.status_code == 200
    assert response.json()["country"] == "USA"
    assert "key_positions" in response.json()

def test_get_policy_invalid():
    response = client.get("/policies/invalid_country")
    assert response.status_code == 404
