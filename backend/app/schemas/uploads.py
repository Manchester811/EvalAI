from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UploadRequest(BaseModel):
    exam_id: Optional[int] = None
    student_id: Optional[int] = None
    # File is passed as multipart upload, not JSON body


class UploadResponse(BaseModel):
    sheet_id: int
    file_key: str
    status: str = "pending"
    message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
