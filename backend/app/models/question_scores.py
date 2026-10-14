from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from app.db.base import Base
from datetime import datetime

class QuestionScore(Base):
    __tablename__ = "question_scores"
    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    awarded_marks = Column(Float, default=0)
    max_marks = Column(Float, default=0)
    rationale = Column(Text)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
