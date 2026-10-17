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
import os as _os


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

# Single versioned registration — no duplicate unversioned routes (dedup)
app.include_router(health_router, tags=['health'])

app.include_router(exams_router)
app.include_router(questions_router)
app.include_router(rubric_criteria_router)
app.include_router(uploads_router)

app.include_router(evaluations_router)
app.include_router(exports_router)
app.include_router(analytics_router)
app.include_router(bulk_router)
app.include_router(students_router)

# Startup: avoid eager create_all for production — use Alembic in production.
# Keep SQLite convenience for dev/tests when ALEMBIC_USE != 1.
_allow_create_all = settings.DATABASE_URL.startswith("sqlite") and _os.getenv("ALEMBIC_USE") != "1"
if _allow_create_all:
    Base.metadata.create_all(bind=engine)


@app.on_event('startup')
async def startup():
    if _allow_create_all:
        Base.metadata.create_all(bind=engine)


@app.on_event('shutdown')
async def shutdown():
    pass

# Extra: readiness check
from fastapi import HTTPException
from app.core.config import settings as _s

@app.get("/ready")
async def readiness():
    # Loose dependency checks — no secrets exposed; just verifies DB and config are valid
    checks = {
        "db": "ok" if _s.DATABASE_URL else "missing",
        "uploads_dir": "ok" if _s.UPLOAD_DIR else "missing",
        "secret_configured": "ok" if _s.SECRET_KEY and _s.SECRET_KEY != "replace-with-long-random-secret" else "default",
    }
    # Return 503 if production secret not set (fail-closed)
    if _s.APP_ENV == "production" and checks["secret_configured"] != "ok":
        raise HTTPException(status_code=503, detail="Not ready: required secrets not configured.")
    return {"status": "ready", "checks": checks}
