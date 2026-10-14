from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from app.db.base import Base
from datetime import datetime

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    prompt = Column(Text, nullable=False)
    reference_answer = Column(Text)
    max_marks = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
