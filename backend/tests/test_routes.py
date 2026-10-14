from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_versioned_resource_routes_are_registered():
    assert client.get('/api/v1/exams/999999').status_code == 404
    assert client.get('/api/v1/questions/999999').status_code == 404
    assert client.get('/api/v1/rubric-criteria/999999').status_code == 404


def test_additional_routers_are_registered():
    assert client.get('/api/v1/analytics/overview').status_code == 200
    assert client.get('/api/v1/batches/missing').status_code == 404
    assert client.get('/api/v1/exports/evaluations').status_code == 200
