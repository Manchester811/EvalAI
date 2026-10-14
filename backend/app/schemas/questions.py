from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class QuestionBase(BaseModel):
    exam_id: int
    question_number: int = Field(..., ge=1)
    prompt: str = Field(..., min_length=1)
    reference_answer: Optional[str] = None
    max_marks: float = Field(default=0, ge=0)

class QuestionCreate(QuestionBase):
    pass

class QuestionOut(QuestionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
