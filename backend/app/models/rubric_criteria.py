from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from app.db.base import Base
from datetime import datetime

class RubricCriterion(Base):
    __tablename__ = "rubric_criteria"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    criterion = Column(String(255), nullable=False)
    max_marks = Column(Float, default=0)
    guidance = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
