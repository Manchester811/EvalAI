from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories import exam_repo as repo
from app.schemas.exams import ExamCreate, ExamOut

from app.core.auth import get_current_user, require_role
from app.core.security import Role

router = APIRouter(prefix="/exams", tags=["exams"])

@router.post("/", response_model=ExamOut)
def create_exam(obj_in: ExamCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_role(Role.faculty, Role.admin))):
    # Create exam linked to authorised faculty; do not trust client user ID
    result = repo.create(db, obj_in)
    # Record created_by from token, not from request
    result.created_by = current_user["id"]
    db.commit()
    db.refresh(result)
    return result

@router.get("/")
def list_exams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repo.get_multi(db, skip, limit)

@router.get("/{exam_id}", response_model=ExamOut)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    obj = repo.get(db, exam_id)
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/{exam_id}", response_model=ExamOut)
def update_exam(exam_id: int, obj_in: ExamCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_role(Role.faculty, Role.admin))):
    obj = repo.get(db, exam_id)
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    if obj.created_by is not None and obj.created_by != current_user["id"] and current_user.get("role") != Role.admin:
        raise HTTPException(status_code=403, detail="Not authorized to modify this exam")
    return repo.update(db, obj, obj_in)

@router.delete("/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_role(Role.faculty, Role.admin))):
    obj = repo.get(db, exam_id)
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    if obj.created_by is not None and obj.created_by != current_user["id"] and current_user.get("role") != Role.admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this exam")
    repo.remove(db, exam_id)
    return {"ok": True}
