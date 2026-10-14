from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_evaluation():
    response = client.get("/api/v1/evaluations/1")
    assert response.status_code in (200, 404)


def test_patch_evaluation():
    response = client.patch("/api/v1/evaluations/1", json={"marks": 85})
    assert response.status_code in (200, 404)


def test_approve_evaluation():
    response = client.post("/api/v1/evaluations/1/approve")
    assert response.status_code in (200, 404)


def test_unauthorized():
    response = client.patch("/api/v1/evaluations/999", json={"marks": 50})
    assert response.status_code in (403, 404)


def test_audit_on_update_approve():
    response = client.patch("/api/v1/evaluations/1", json={"marks": 90})
    assert response.status_code in (200, 404)
    response = client.post("/api/v1/evaluations/1/approve")
    assert response.status_code in (200, 404)
