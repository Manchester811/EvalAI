import mimetypes
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.schemas.uploads import UploadResponse
from app.services import storage
from app.models.answer_sheets import AnswerSheet

from app.core.auth import get_current_user, require_role
from app.core.security import Role

router = APIRouter(prefix='/api/v1', tags=['uploads'])

ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'application/pdf'}
ALLOWED_EXTS = {'.jpg', '.jpeg', '.png', '.pdf'}


def _validate_content(file_bytes: bytes, filename: str) -> None:
    # Validate by content / MIME, not just extension (FR-04; ARCHITECTURE �10 step 1)
    # Check magic bytes for JPG/PNG/PDF
    if file_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        detected = 'image/png'
    elif file_bytes[:2] == b'\xff\xd8':
        detected = 'image/jpeg'
    elif file_bytes[:4] == b'%PDF':
        detected = 'application/pdf'
    else:
        detected = None
    if detected not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail='Invalid file content/type (expected JPG/PNG/PDF)')


@router.post('/answer-sheets', response_model=UploadResponse)
async def upload_answer_sheet(
    file: UploadFile = File(...),
    exam_id: int = Form(None),
    student_id: int = Form(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(Role.faculty, Role.admin)),
):
    # Read bytes (limit enforced by server / middleware; enforce MAX_UPLOAD_MB here)
    raw = await file.read()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(raw) > max_bytes:
        raise HTTPException(status_code=413, detail=f'File exceeds {settings.MAX_UPLOAD_MB} MB')

    # Enforce page count / basic sanity (stub: no full processing yet -- upload + validation only)
    # For PDF, could count pages via PyPDF2; kept stub per instruction

    # Content validation (FR-04)
    _validate_content(raw, file.filename or 'unknown')

    # Generate private file key; save to private storage (FR-04; ARCHITECTURE �11)
    file_key = storage.generate_file_key(file.filename or 'upload')
    storage.save_upload_file(raw, file_key)

    # Store reference privately; never expose file path / credentials to browser (FR-06; ARCHITECTURE �3)
    sheet = AnswerSheet(
        exam_id=exam_id,
        student_id=student_id,
        original_file_key=file_key,
        status='pending',
        uploaded_by=None  # could use auth header in full build
    )
    try:
        db.add(sheet)
        db.commit()
    except Exception:
        db.rollback()
        storage.delete_file(file_key)
        raise
    db.refresh(sheet)

    return UploadResponse(
        sheet_id=sheet.id,
        file_key=file_key,
        status=sheet.status,
        message='Upload accepted; processing deferred'
    )
