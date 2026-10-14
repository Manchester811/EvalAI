from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RubricCriterionBase(BaseModel):
    question_id: int
    criterion: str = Field(..., min_length=1, max_length=255)
    max_marks: float = Field(default=0, ge=0)
    guidance: Optional[str] = None

class RubricCriterionCreate(RubricCriterionBase):
    pass

class RubricCriterionOut(RubricCriterionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
