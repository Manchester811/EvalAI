from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean
from app.db.base import Base
from datetime import datetime

class Evaluation(Base):
    __tablename__ = 'evaluations'
    id = Column(Integer, primary_key=True, index=True)
    answer_sheet_id = Column(Integer, ForeignKey('answer_sheets.id'), nullable=False)
    total_score = Column(Float, default=0)
    status = Column(String(50), default='draft')
    reviewed_by = Column(Integer, ForeignKey('users.id'))
    finalized_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
