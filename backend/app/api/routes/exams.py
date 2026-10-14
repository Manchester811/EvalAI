from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories import exam_repo as repo
from app.schemas.exams import ExamCreate, ExamOut

router = APIRouter(prefix="/exams", tags=["exams"])

@router.post("/", response_model=ExamOut)
def create_exam(obj_in: ExamCreate, db: Session = Depends(get_db)):
    return repo.create(db, obj_in)

@router.get("/")
def list_exams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repo.get_multi(db, skip, limit)

@router.get("/{exam_id}", response_model=ExamOut)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    obj = repo.get(db, exam_id)
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/{exam_id}", response_model=ExamOut)
def update_exam(exam_id: int, obj_in: ExamCreate, db: Session = Depends(get_db)):
    obj = repo.get(db, exam_id)
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    return repo.update(db, obj, obj_in)

@router.delete("/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    obj = repo.get(db, exam_id)
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    repo.remove(db, exam_id)
    return {"ok": True}
