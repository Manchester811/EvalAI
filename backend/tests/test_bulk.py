# Tests for bulk evaluation (FR-10 / ARCHITECTURE §5 Flow B / §6)
import pytest
from app.services.batch import create_batch, retry_failed, BatchItem, JobStatus

def test_batch_create():
    batch = create_batch(["file1.pdf", "file2.pdf"], exam_id=1)
    assert batch.id.startswith("batch-")
    assert len(batch.items) == 2
    assert batch.progress()["total"] == 2

def test_retry_skips_approved():
    batch = create_batch(["a.pdf"])
    # Simulate approved completed item
    batch.items[0].status = JobStatus.completed
    batch.items[0].result = type("R", (), {"status": "approved"})()
    # Add a failed item
    batch.items.append(BatchItem("b.pdf", status=JobStatus.failed))
    result = retry_failed(batch, skip_approved=True)
    assert result["skipped_approved"] == 1
    assert result["retried"] == 1
    # Approved not duplicated (status remains completed)
    assert batch.items[0].status == JobStatus.completed
    assert batch.items[1].status == JobStatus.queued
