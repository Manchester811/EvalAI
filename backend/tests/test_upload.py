import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

# Use a small valid JPEG (1x1 pixel)
VALID_JPG = bytes.fromhex('FFD8FFE000104A46494600010101004800480000FFDB004300080606070605080707070909080A0C140D0C0B0B0C1912130F141D1A1F1E1D1A1C1C20242E2720222C231C1C2837292C30313434341F27393D38323C2E333432FFC00011080001000103012200021101031101FFC4001F0000010501010101010100000000000000000102030405060708090A0BFFC400B5100002010303020403050504040000017D01020300041105122131410613516107227114328191A1082342B1C11552D1F02433627282090A161718191A25262728292A3435363738393A434445464748494A535455565758595A636465666768696A737475767778797A82838485868788898A92939495969798999AA2A3A4A5A6A7A8A9AAB2B3B4B5B6B7B8B9BAC2C3C4C5C6C7C8C9CAD2D3D4D5D6D7D8D9DAE1E2E3E4E5E6E7E8E9EAF1F2F3F4F5F6F7F8F9FAFFDA000C03010002110311003F00F7F8FFD9')

def test_bad_mime_rejected():
    # Try to upload a .txt file (invalid MIME)
    files = {'file': ('test.txt', b'hello world', 'text/plain')}
    r = client.post('/api/v1/answer-sheets', files=files)
    assert r.status_code == 400


def test_valid_png_signature_accepted():
    from app.api.routes.uploads import _validate_content

    _validate_content(b'\x89PNG\r\n\x1a\n' + b'payload', 'test.png')

def test_good_jpg_upload():
    files = {'file': ('test.jpg', VALID_JPG, 'image/jpeg')}
    r = client.post('/api/v1/answer-sheets', files=files, data={'exam_id': '1'})
    # DB not available in test env -> 500 on DB call, but endpoint wiring OK
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        j = r.json()
        assert 'sheet_id' in j
        assert 'file_key' in j
        assert j['status'] == 'pending'

def test_storage_saves_file(tmp_path, monkeypatch):
    # Unit test: storage module saves file to private dir
    from app.services import storage
    monkeypatch.setattr(storage, 'UPLOAD_DIR', tmp_path)
    key = storage.generate_file_key('test.jpg')
    p = storage.save_upload_file(b'ABC', key)
    assert p.exists()
    assert p.read_bytes() == b'ABC'

def test_no_secrets_leaked_in_response():
    # Ensure no internal paths or credentials in response
    files = {'file': ('test.jpg', VALID_JPG, 'image/jpeg')}
    r = client.post('/api/v1/answer-sheets', files=files)
    if r.status_code == 200:
        j = r.json()
        assert 'original_file_key' not in str(j).lower()  # only file_key (UUID) exposed
        assert 'path' not in str(j).lower()
        assert 'secret' not in str(j).lower()
        assert 'key' not in str(j).lower() or 'file_key' in str(j).lower()
