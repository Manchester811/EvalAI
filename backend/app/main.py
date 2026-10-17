from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.health import router as health_router
from app.api.routes.exams import router as exams_router
from app.api.routes.questions import router as questions_router
from app.api.routes.rubric_criteria import router as rubric_criteria_router
from app.api.routes.uploads import router as uploads_router
from app.api.routes.evaluations import router as evaluations_router
from app.api.routes.exports import router as exports_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.bulk import router as bulk_router
from app.api.routes.students import router as students_router
from app.db.session import engine
from app.db.base import Base
from app.core.config import settings
import app.models  # noqa: F401 - register every model before create_all

app = FastAPI()

allowed = [settings.FRONTEND_ORIGIN] if settings.FRONTEND_ORIGIN else []
if settings.APP_ENV == "development":
    allowed = list({*allowed, "http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:8000"})
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)
app.include_router(health_router, tags=['health'])
app.include_router(exams_router)
app.include_router(exams_router, prefix="/api/v1")
app.include_router(questions_router)
app.include_router(questions_router, prefix="/api/v1")
app.include_router(rubric_criteria_router)
app.include_router(rubric_criteria_router, prefix="/api/v1")
app.include_router(uploads_router)
app.include_router(evaluations_router)
app.include_router(exports_router)
app.include_router(analytics_router)
app.include_router(bulk_router)
app.include_router(students_router)

# TestClient requests do not always enter the ASGI lifespan context. Creating
# the local SQLite schema eagerly keeps a fresh development checkout usable;
# production PostgreSQL deployments should use Alembic migrations instead.
if settings.DATABASE_URL.startswith("sqlite"):
    Base.metadata.create_all(bind=engine)

@app.on_event('startup')
async def startup():
    Base.metadata.create_all(bind=engine)

@app.on_event('shutdown')
async def shutdown():
    pass
