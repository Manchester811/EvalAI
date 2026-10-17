from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.models.students import Student
from app.core.auth import require_role
from app.core.security import Role

router = APIRouter(prefix="/api/v1/students", tags=["students"])

@router.get("/")
def list_students(db: Session = Depends(get_db), current_user: dict = Depends(require_role(Role.faculty, Role.admin)), search: Optional[str] = Query(None)):
    q = db.query(Student)
    if search:
        pattern = f"%{search}%"
        q = q.filter((Student.name.ilike(pattern)) | (Student.student_number.ilike(pattern)))
    results = q.order_by(Student.created_at.desc()).limit(100).all()
    return [
        {
            "id": s.id,
            "student_number": s.student_number,
            "name": s.name,
            "class_or_section": s.class_or_section,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in results
    ]

@router.post("/")
def create_student(student_number: str, name: str, class_or_section: Optional[str] = None, db: Session = Depends(get_db), current_user: dict = Depends(require_role(Role.faculty, Role.admin))):
    if db.query(Student).filter(Student.student_number == student_number).first():
        raise HTTPException(status_code=400, detail="Student number already exists.")
    student = Student(student_number=student_number, name=name, class_or_section=class_or_section)
    db.add(student)
    db.commit()
    db.refresh(student)
    return {"id": student.id, "student_number": student.student_number, "name": student.name, "class_or_section": student.class_or_section}

@router.get("/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_role(Role.faculty, Role.admin))):
    s = db.query(Student).filter(Student.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Not found.")
    return {"id": s.id, "student_number": s.student_number, "name": s.name, "class_or_section": s.class_or_section}

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_role(Role.faculty, Role.admin))):
    s = db.query(Student).filter(Student.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Not found.")
    db.delete(s)
    db.commit()
    return {"ok": True}
