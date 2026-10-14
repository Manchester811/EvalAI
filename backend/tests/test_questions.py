from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_create_question():
    r = client.post("/exams/", json={"title": "Quiz", "total_marks": 50})
    exam_id = r.json()["id"]
    r2 = client.post("/questions/", json={"exam_id": exam_id, "question_number": 1, "prompt": "Q1", "max_marks": 10})
    assert r2.status_code == 200
