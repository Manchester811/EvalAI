import os
import uuid
from pathlib import Path
from typing import Optional
from app.core.config import settings

UPLOAD_DIR = Path(settings.UPLOAD_DIR).resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def generate_file_key(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return unique_name


def save_upload_file(file_bytes: bytes, file_key: str) -> Path:
    file_path = UPLOAD_DIR / file_key
    file_path.write_bytes(file_bytes)
    return file_path


def get_file_path(file_key: str) -> Optional[Path]:
    file_path = UPLOAD_DIR / file_key
    if file_path.exists():
        return file_path
    return None


def delete_file(file_key: str) -> bool:
    file_path = UPLOAD_DIR / file_key
    if file_path.exists():
        file_path.unlink()
        return True
    return False


def get_file_size(file_key: str) -> Optional[int]:
    file_path = UPLOAD_DIR / file_key
    if file_path.exists():
        return file_path.stat().st_size
    return None
