from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from app.db.base import Base
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(255), nullable=False)
    entity_type = Column(String(100))
    entity_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
