from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from app.db.base import Base
from datetime import datetime

class FeedbackItem(Base):
    __tablename__ = "feedback_items"
    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=False)
    category = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
