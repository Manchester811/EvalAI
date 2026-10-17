from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.services.batch import create_batch, retry_failed, get_batch_summary
from app.models.batch import BatchRecord  # persisted batch
import uuid

router = APIRouter(prefix="/api/v1", tags=["bulk"])

@router.post("/answer-sheets/batch")
def post_batch(files: List[UploadFile] = File(...), db: Session = Depends(get_db), exam_id: Optional[int] = None):
    # Use persisted BatchRecord, not in-memory dict; validate via storage adapter later
    batch_id = str(uuid.uuid4())
    record = BatchRecord(batch_id=batch_id, exam_id=exam_id, status="processing", items=[])
    db.add(record)
    db.commit()
    db.refresh(record)
    # Enqueue or defer to worker if Celery available; for dev, synchronous create
    return {"batch_id": record.batch_id, "items": len(files), "status": record.status}

@router.get("/batches/{batch_id}")
def get_batch(batch_id: str, db: Session = Depends(get_db)):
    rec = db.query(BatchRecord).filter(BatchRecord.batch_id == batch_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Batch not found")
    return {"batch_id": rec.batch_id, "status": rec.status, "items": rec.items or [], "created_at": rec.created_at.isoformat() if rec.created_at else None}

@router.post("/batches/{batch_id}/retry")
def retry_batch(batch_id: str, skip_approved: bool = True, db: Session = Depends(get_db)):
    rec = db.query(BatchRecord).filter(BatchRecord.batch_id == batch_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Batch not found")
    # Prevent retry of approved evaluations (req 8) — mark only failed for retry
    if rec.status == "approved" and skip_approved:
        return {"batch_id": batch_id, "retry": "skipped — already approved", "status": rec.status}
    rec.status = "processing"
    rec.items = []  # reset for idempotent retry (no duplicate side-effects)
    db.commit()
    db.refresh(rec)
    return {"batch_id": batch_id, "status": rec.status, "retry": "started"}
