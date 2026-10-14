from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from app.db.base import Base
from datetime import datetime

class ExtractedAnswer(Base):
    __tablename__ = "extracted_answers"
    id = Column(Integer, primary_key=True, index=True)
    answer_sheet_id = Column(Integer, ForeignKey("answer_sheets.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    extracted_text = Column(Text)
    ocr_confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
