# Batch service: bulk evaluation + status tracking (FR-10 / ARCHITECTURE §5 Flow B / §6)
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class BatchItem:
    def __init__(self, file_key: str, status=JobStatus.queued):
        self.file_key = file_key
        self.status = status
        self.result = None
        self.error = None

class Batch:
    def __init__(self, batch_id, items, exam_id=None):
        self.id = batch_id
        self.items = items
        self.exam_id = exam_id
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
    def progress(self):
        total = len(self.items)
        if total == 0: return {"total":0,"completed":0,"failed":0,"progress_pct":0.0}
        completed = sum(1 for i in self.items if i.status == JobStatus.completed)
        failed = sum(1 for i in self.items if i.status == JobStatus.failed)
        return {"total":total,"completed":completed,"failed":failed,"progress_pct":round(100.0*completed/total,1)}

def create_batch(files, exam_id=None):
    return Batch("batch-"+datetime.utcnow().strftime("%Y%m%d%H%M%S%f"), [BatchItem(f) for f in files], exam_id)

def retry_failed(batch, skip_approved=True):
    retried = 0; skipped = 0
    for item in batch.items:
        if item.status == JobStatus.failed:
            item.status = JobStatus.queued; item.error = None; retried += 1
        elif skip_approved and item.status == JobStatus.completed and item.result and getattr(item.result, "status", None) == "approved":
            skipped += 1
    batch.updated_at = datetime.utcnow()
    return {"retried": retried, "skipped_approved": skipped, "progress": batch.progress()}

def get_batch_summary(batch):
    return {"batch_id":batch.id,"exam_id":batch.exam_id,"created_at":batch.created_at.isoformat(),"updated_at":batch.updated_at.isoformat(),"items":[{"file_key":i.file_key,"status":i.status.value,"has_result":i.result is not None,"error":i.error} for i in batch.items],"progress":batch.progress()}
