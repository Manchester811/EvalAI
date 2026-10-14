from sqlalchemy.orm import Session
from app.models.questions import Question
from app.models.exams import Exam
from app.schemas.questions import QuestionCreate

def get(db: Session, question_id: int):
    return db.query(Question).filter(Question.id == question_id).first()

def get_multi(db: Session, skip=0, limit=100):
    return db.query(Question).offset(skip).limit(limit).all()

def create(db: Session, obj_in: QuestionCreate):
    exam = db.query(Exam).filter(Exam.id == obj_in.exam_id).first()
    if exam and exam.total_marks > 0 and obj_in.max_marks > exam.total_marks:
        raise ValueError('Question max_marks exceeds exam total_marks')
    db_obj = Question(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: Question, obj_in: QuestionCreate):
    exam = db.query(Exam).filter(Exam.id == obj_in.exam_id).first()
    if exam and exam.total_marks > 0 and obj_in.max_marks > exam.total_marks:
        raise ValueError('Question max_marks exceeds exam total_marks')
    for k,v in obj_in.model_dump(exclude_unset=True).items():
        setattr(db_obj, k, v)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, question_id: int):
    obj = db.query(Question).filter(Question.id == question_id).first()
    if obj:
        db.delete(obj)
        db.commit()
    return obj
