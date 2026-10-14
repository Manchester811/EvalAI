from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/overview")
def analytics_overview(
    exam_id: Optional[int] = Query(None, description="Filter by exam ID"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    db: Session = Depends(get_db)
):
    svc = AnalyticsService(db)
    return svc.overview(exam_id=exam_id, subject_filter=subject)
