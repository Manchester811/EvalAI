from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_create_criterion():
    r = client.post("/exams/", json={"title": "E", "total_marks": 10})
    exam_id = r.json()["id"]
    r2 = client.post("/questions/", json={"exam_id": exam_id, "question_number": 1, "prompt": "Q", "max_marks": 5})
    q_id = r2.json()["id"]
    r3 = client.post("/rubric-criteria/", json={"question_id": q_id, "criterion": "Accuracy", "max_marks": 5})
    assert r3.status_code == 200
