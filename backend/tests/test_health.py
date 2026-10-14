import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
