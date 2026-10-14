from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from app.db.base import Base
from datetime import datetime

class AnswerSheet(Base):
    __tablename__ = "answer_sheets"
    id = Column(Integer, primary_key=True, index=True)
    # Uploads can be staged before a faculty member assigns an exam.
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    original_file_key = Column(String(500))
    status = Column(String(50), default="pending")
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
