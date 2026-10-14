from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.evaluations import Evaluation
from app.services.audit import log_audit_event


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
def get_evaluation(evaluation_id: int, db: Session = Depends(get_db)):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return _serialize(evaluation)


@router.patch("/{evaluation_id}")
def update_evaluation(
    evaluation_id: int,
    changes: EvaluationUpdate,
    db: Session = Depends(get_db),
    user_id: int = 1,
):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    new_score = changes.total_score if changes.total_score is not None else changes.marks
    if new_score is None:
        raise HTTPException(status_code=400, detail="Provide marks or total_score")

    previous_score = evaluation.total_score
    evaluation.total_score = new_score
    try:
        db.commit()
        db.refresh(evaluation)
        log_audit_event(
            db=db,
            user_id=user_id,
            action="evaluation_update",
            entity_type="evaluation",
            entity_id=evaluation_id,
            details={"previous": previous_score, "updated": new_score},
        )
    except Exception:
        db.rollback()
        raise
    return {**_serialize(evaluation), "updated": True, "previous_value": previous_score}


@router.post("/{evaluation_id}/approve")
def approve_evaluation(evaluation_id: int, db: Session = Depends(get_db), user_id: int = 1):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")

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
