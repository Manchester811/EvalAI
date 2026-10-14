from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Float, Enum as SAEnum, Index
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
from app.core.security import Role

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(Role), default=Role.faculty, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
