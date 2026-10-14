from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.services.exports import ExportService
from app.core.security import Role

router = APIRouter(prefix="/api/v1/exports", tags=["exports"])

def get_current_user():
    return {"id": 1, "role": Role.faculty}

@router.get("/evaluations")
def export_evaluations(
    exam_id: Optional[int] = Query(None, description="Filter by exam ID"),
    student_id: Optional[int] = Query(None, description="Filter by student ID"),
    format: str = Query("csv", description="Export format: csv or pdf"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    service = ExportService(db, current_user["id"], current_user["role"])
    try:
        if format.lower() == "csv":
            csv_data = service.export_evaluations_csv(exam_id=exam_id, student_id=student_id)
            from fastapi.responses import Response
            return Response(
                content=csv_data,
                media_type="text/csv; charset=utf-8",
                headers={"Content-Disposition": "attachment; filename=evaluations_export.csv"}
            )
        elif format.lower() == "pdf":
            pdf_data = service.export_evaluations_pdf_stub(exam_id=exam_id, student_id=student_id)
            from fastapi.responses import Response
            return Response(
                content=pdf_data,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=evaluations_export.pdf"}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'csv' or 'pdf'")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
