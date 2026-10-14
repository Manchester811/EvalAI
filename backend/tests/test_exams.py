from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_create_exam():
    r = client.post("/exams/", json={"title": "Math", "total_marks": 100})
    assert r.status_code == 200

def test_list_exams():
    r = client.get("/exams/")
    assert r.status_code == 200
