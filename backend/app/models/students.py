from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    class_or_section = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
