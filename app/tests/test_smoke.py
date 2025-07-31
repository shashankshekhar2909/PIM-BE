from fastapi.testclient import TestClient
from app.main import app

def test_root():
    client = TestClient(app)
    response = client.get("/api/v1/auth/me")
    assert response.status_code in (200, 401) 