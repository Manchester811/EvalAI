from sqlalchemy.orm import Session
from app.models.exams import Exam
from app.schemas.exams import ExamCreate

def get(db: Session, exam_id: int):
    return db.query(Exam).filter(Exam.id == exam_id).first()

def get_multi(db: Session, skip=0, limit=100):
    return db.query(Exam).offset(skip).limit(limit).all()

def create(db: Session, obj_in: ExamCreate):
    db_obj = Exam(**obj_in.model_dump())
    db.add(db_obj); db.commit(); db.refresh(db_obj); return db_obj

def update(db: Session, db_obj: Exam, obj_in: ExamCreate):
    for k,v in obj_in.model_dump(exclude_unset=True).items(): setattr(db_obj, k, v)
    db.add(db_obj); db.commit(); db.refresh(db_obj); return db_obj

def remove(db: Session, exam_id: int):
    obj = db.query(Exam).filter(Exam.id == exam_id).first()
    if obj: db.delete(obj); db.commit()
    return obj
