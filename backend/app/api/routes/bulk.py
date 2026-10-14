from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.services.batch import create_batch, retry_failed, get_batch_summary

router = APIRouter(prefix="/api/v1", tags=["bulk"])

# In-memory batch store for wiring verification (DB unavailable expected)
batches = {}

@router.post("/answer-sheets/batch")
def post_batch(files: List[UploadFile] = File(...), db: Session = Depends(get_db), exam_id: Optional[int] = None):
    file_keys = [f.filename for f in files]
    batch = create_batch(file_keys, exam_id=exam_id)
    batches[batch.id] = batch
    return {"batch_id": batch.id, "items": len(batch.items), "progress": batch.progress()}

@router.get("/batches/{batch_id}")
def get_batch(batch_id: str, db: Session = Depends(get_db)):
    if batch_id not in batches:
        raise HTTPException(status_code=404, detail="Batch not found")
    return get_batch_summary(batches[batch_id])

@router.post("/batches/{batch_id}/retry")
def retry_batch(batch_id: str, skip_approved: bool = True, db: Session = Depends(get_db)):
    if batch_id not in batches:
        raise HTTPException(status_code=404, detail="Batch not found")
    result = retry_failed(batches[batch_id], skip_approved=skip_approved)
    return {"batch_id": batch_id, "retry_result": result}
