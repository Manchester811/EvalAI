import mimetypes
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.core.auth import get_current_user, require_role
from app.core.security import Role
from app.schemas.uploads import UploadResponse
from app.services import storage
from app.services.storage import UPLOAD_DIR
from app.models.answer_sheets import AnswerSheet
from app.services.ocr.adapter import get_ocr_provider
from app.services.scoring import evaluate_answer
import math
import tempfile

router = APIRouter(prefix='/api/v1', tags=['uploads'])

ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'application/pdf'}
ALLOWED_EXTS = {'.jpg', '.jpeg', '.png', '.pdf'}


def _validate_content(file_bytes: bytes, filename: str) -> None:
    if not file_bytes or len(file_bytes) < 4:
        raise HTTPException(status_code=400, detail='File is empty or truncated.')
    if file_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        detected = 'image/png'
    elif file_bytes[:2] == b'\xff\xd8':
        detected = 'image/jpeg'
    elif file_bytes[:4] == b'%PDF':
        detected = 'application/pdf'
    else:
        raise HTTPException(status_code=400, detail='Invalid or unsupported file signature.')
    if detected not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail='Unsupported file type.')
    declared_ext = Path(filename).suffix.lower()
    if declared_ext in ALLOWED_EXTS:
        if declared_ext in ('.jpg', '.jpeg') and detected != 'image/jpeg':
            raise HTTPException(status_code=400, detail='File extension does not match content.')
        if declared_ext == '.png' and detected != 'image/png':
            raise HTTPException(status_code=400, detail='File extension does not match content.')
        if declared_ext == '.pdf' and detected != 'application/pdf':
            raise HTTPException(status_code=400, detail='File extension does not match content.')


@router.post('/answer-sheets', response_model=UploadResponse)
async def upload_answer_sheet(
    file: UploadFile = File(...),
    exam_id: int = Form(None),
    student_id: int = Form(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(Role.faculty, Role.admin)),
):
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    chunks = []
    total_read = 0
    chunk_size = 65536
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total_read += len(chunk)
        if total_read > max_bytes:
            raise HTTPException(status_code=413, detail=f'File exceeds {settings.MAX_UPLOAD_MB} MB')
        chunks.append(chunk)
    raw = b''.join(chunks)

    _validate_content(raw, file.filename or 'unknown')

    try:
        if raw[:4] == b'%PDF':
            import re
            pages = len(re.findall(b'/Type\\s*/Page[^s]', raw[:50000], re.ASCII))
            if pages > 20:
                raise HTTPException(status_code=400, detail='PDF exceeds 20 pages.')
    except HTTPException:
        raise

    file_key = storage.generate_file_key(file.filename or 'upload')
    file_path = UPLOAD_DIR / file_key
    try:
        file_path.resolve().relative_to(UPLOAD_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid storage path.')

    try:
        storage.save_upload_file(raw, file_key)
    except Exception:
        raise HTTPException(status_code=500, detail='Storage failure.')

    if exam_id is not None:
        from app.models.exams import Exam
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if exam is None:
            storage.delete_file(file_key)
            raise HTTPException(status_code=404, detail='Exam not found.')
        if exam.created_by is not None and exam.created_by != current_user.get('id') and current_user.get('role') != Role.admin:
            storage.delete_file(file_key)
            raise HTTPException(status_code=403, detail='Not authorized for this exam.')

    sheet = AnswerSheet(
        exam_id=exam_id,
        student_id=student_id,
        original_file_key=file_key,
        status='pending',
        uploaded_by=current_user.get('id'),
        file_size_bytes=total_read,
    )
    try:
        db.add(sheet)
        db.commit()
        db.refresh(sheet)
    except Exception:
        db.rollback()
        storage.delete_file(file_key)
        raise HTTPException(status_code=500, detail='DB failure; file cleaned.')

    try:
        from app.services.ocr.adapter import get_ocr_provider
        provider = get_ocr_provider()
        extracted = provider.extract_text(str(file_path))
        from app.models.extracted_answers import ExtractedAnswer
        for item in (extracted or []):
            db.add(ExtractedAnswer(
                answer_sheet_id=sheet.id,
                question_id=1,
                extracted_text=item.get('text', ''),
                confidence=item.get('confidence', 0.0),
            ))
        sheet.status = 'processing'
        db.commit()
        db.refresh(sheet)
        msg = 'Upload accepted; OCR processing started (observable).'
    except Exception as exc:
        sheet.status = 'needs_review'
        try:
            db.add(sheet)
            db.commit()
        except Exception:
            pass
        msg = f"Upload accepted; processing deferred (OCR error: {str(exc)}). Manual review required."

    return UploadResponse(
        sheet_id=sheet.id,
        file_key=file_key,
        status=sheet.status,
        message=msg,
    )
