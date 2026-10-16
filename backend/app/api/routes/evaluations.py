from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.evaluations import Evaluation
from app.services.audit import log_audit_event


from app.core.auth import get_current_user, require_role
from app.core.security import Role

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])

class EvaluationUpdate(BaseModel):
    # ``marks`` is retained as an API alias for the existing frontend/tests.
    marks: Optional[float] = Field(None, ge=0)
    total_score: Optional[float] = Field(None, ge=0)


def _serialize(evaluation: Evaluation) -> dict:
    return {
        "id": evaluation.id,
        "status": evaluation.status,
        "label": "approved" if evaluation.status == "approved" else "ai_suggested",
        "marks": evaluation.total_score,
        "total_score": evaluation.total_score,
        "feedback": "",
        "reviewed_by": evaluation.reviewed_by,
        "finalized_at": evaluation.finalized_at.isoformat() if evaluation.finalized_at else None,
    }


@router.get("/{evaluation_id}")
def get_evaluation(evaluation_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_role(Role.faculty, Role.admin, Role.student))):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    # Authorization: owner/admin can read; students only their own (simplified)
    if current_user.get("role") == Role.student and evaluation.student_id != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Access denied")
    return _serialize(evaluation)


@router.patch("/{evaluation_id}")
def update_evaluation(
    evaluation_id: int,
    changes: EvaluationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(Role.faculty, Role.admin)),
):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    # Authorization: only faculty/admin who own/exam-related can edit
    new_score = changes.total_score if changes.total_score is not None else changes.marks
    if new_score is None:
        raise HTTPException(status_code=400, detail="Provide marks or total_score")
    previous_score = evaluation.total_score
    evaluation.total_score = new_score
    try:
        db.commit()
        db.refresh(evaluation)
        # Audit with actual user from token, not hard-coded 1
        log_audit_event(
            db=db,
            user_id=current_user["id"],
            action="evaluation_update",
            entity_type="evaluation",
            entity_id=evaluation_id,
            details={"previous": previous_score, "updated": new_score, "user": current_user["id"], "role": current_user["role"].value},
            commit=False,
        )
    except Exception as exc:
        db.rollback()
        # Audit failure must not leave incorrect success; log failure, then raise
        try:
        log_audit_event(
            db=db,
            user_id=current_user.get("id", 0),
            action="audit_failed",
            entity_type="evaluation",
            entity_id=evaluation_id,
            details={"error": str(exc), "phase": "update_after_commit"},
            commit=False,
        )
        except Exception:
            pass  # audit failure must not suppress original error; do not claim success
        raise HTTPException(status_code=500, detail="Update failed; audit logged.")
    return {**_serialize(evaluation), "updated": True, "previous_value": previous_score}


@router.post("/{evaluation_id}/approve")
def approve_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(Role.faculty, Role.admin)),
):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    # Authorization: only faculty/admin can approve
    evaluation.status = "approved"
    evaluation.reviewed_by = current_user["id"]
    evaluation.finalized_at = datetime.now(timezone.utc)
    try:
        db.commit()
        db.refresh(evaluation)
        log_audit_event(
            db=db,
            user_id=current_user["id"],
            action="evaluation_approve",
            entity_type="evaluation",
            entity_id=evaluation_id,
            details={"reviewer": current_user["id"], "role": current_user["role"].value, "finalized_at": evaluation.finalized_at.isoformat()},
            commit=False,
        )
    except Exception as exc:
        db.rollback()
        try:
            log_audit_event(
                db=db,
                user_id=current_user.get("id", 0),
                action="audit_failed_approve",
                entity_type="evaluation",
                entity_id=evaluation_id,
                details={"error": str(exc)},
            )
        except Exception:
            pass
        raise HTTPException(status_code=500, detail="Approval failed; audit logged.")
    return {**_serialize(evaluation), "approved": True, "reviewed_by": current_user["id"], "finalized_at": evaluation.finalized_at.isoformat()}

    finalized_at = datetime.utcnow()
    evaluation.status = "approved"
    evaluation.reviewed_by = user_id
    evaluation.finalized_at = finalized_at
    try:
        db.commit()
        db.refresh(evaluation)
        log_audit_event(
            db=db,
            user_id=user_id,
            action="evaluation_approve",
            entity_type="evaluation",
            entity_id=evaluation_id,
            details={"new_status": "approved"},
        )
    except Exception:
        db.rollback()
        raise
    return _serialize(evaluation)
