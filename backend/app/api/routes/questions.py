from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories import question_repo as repo
from app.schemas.questions import QuestionCreate, QuestionOut

router = APIRouter(prefix="/questions", tags=["questions"])

@router.post("/", response_model=QuestionOut)
def create_question(obj_in: QuestionCreate, db: Session = Depends(get_db)):
    return repo.create(db, obj_in)

@router.get("/")
def list_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repo.get_multi(db, skip, limit)

@router.get("/{question_id}", response_model=QuestionOut)
def get_question(question_id: int, db: Session = Depends(get_db)):
    obj = repo.get(db, question_id)
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/{question_id}", response_model=QuestionOut)
def update_question(question_id: int, obj_in: QuestionCreate, db: Session = Depends(get_db)):
    obj = repo.get(db, question_id)
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    return repo.update(db, obj, obj_in)

@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    obj = repo.get(db, question_id)
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    repo.remove(db, question_id)
    return {"ok": True}
