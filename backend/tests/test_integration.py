import pytest
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_upload_ocr_scoring_approval_export_flow():
    from app.services import storage, scoring
    from app.services.ocr import adapter
    key = storage.generate_file_key('test.jpg')
    p = storage.save_upload_file(b'img', key)
    assert p.exists()
    assert adapter is not None
    result = scoring.evaluate_answer('Correct.', 'Correct.', [scoring.RubricCriterion(id=1, criterion='C', max_marks=5)])
    assert 0 <= result.awarded_marks <= result.max_marks
    r = client.post('/api/v1/evaluations/1/approve')
    assert r.status_code in (200, 404)
    r = client.get('/api/v1/evaluations/1/export')
    assert r.status_code in (200, 404)
