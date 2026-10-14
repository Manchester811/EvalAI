from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ExamBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    subject: Optional[str] = Field(None, max_length=255)
    exam_date: Optional[datetime] = None
    total_marks: float = Field(default=0, ge=0)
    created_by: Optional[int] = None

class ExamCreate(ExamBase):
    pass

class ExamOut(ExamBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
