from sqlalchemy.orm import Session
from app.models.rubric_criteria import RubricCriterion
from app.schemas.rubric_criteria import RubricCriterionCreate

def get(db: Session, criterion_id: int):
    return db.query(RubricCriterion).filter(RubricCriterion.id == criterion_id).first()

def get_multi(db: Session, skip=0, limit=100):
    return db.query(RubricCriterion).offset(skip).limit(limit).all()

def create(db: Session, obj_in: RubricCriterionCreate):
    db_obj = RubricCriterion(**obj_in.model_dump())
    db.add(db_obj); db.commit(); db.refresh(db_obj); return db_obj

def update(db: Session, db_obj: RubricCriterion, obj_in: RubricCriterionCreate):
    for k,v in obj_in.model_dump(exclude_unset=True).items(): setattr(db_obj, k, v)
    db.add(db_obj); db.commit(); db.refresh(db_obj); return db_obj

def remove(db: Session, criterion_id: int):
    obj = db.query(RubricCriterion).filter(RubricCriterion.id == criterion_id).first()
    if obj: db.delete(obj); db.commit()
    return obj
