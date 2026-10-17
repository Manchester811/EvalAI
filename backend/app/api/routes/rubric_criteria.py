from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories import rubric_criterion_repo as repo
from app.schemas.rubric_criteria import RubricCriterionCreate, RubricCriterionOut

router = APIRouter(prefix="/api/v1/rubric-criteria", tags=["rubric_criteria"])

@router.post("/", response_model=RubricCriterionOut)
def create_criterion(obj_in: RubricCriterionCreate, db: Session = Depends(get_db)):
    return repo.create(db, obj_in)

@router.get("/")
def list_criteria(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repo.get_multi(db, skip, limit)

@router.get("/{criterion_id}", response_model=RubricCriterionOut)
def get_criterion(criterion_id: int, db: Session = Depends(get_db)):
    obj = repo.get(db, criterion_id)
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    return obj

@router.put("/{criterion_id}", response_model=RubricCriterionOut)
def update_criterion(criterion_id: int, obj_in: RubricCriterionCreate, db: Session = Depends(get_db)):
    obj = repo.get(db, criterion_id)
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    return repo.update(db, obj, obj_in)

@router.delete("/{criterion_id}")
def delete_criterion(criterion_id: int, db: Session = Depends(get_db)):
    obj = repo.get(db, criterion_id)
    if not obj: raise HTTPException(status_code=404, detail="Not found")
    repo.remove(db, criterion_id)
    return {"ok": True}
