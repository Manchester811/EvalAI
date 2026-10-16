# EvalAI — Run Steps

## Prerequisites
Node LTS + Python 3.11 + (optional Docker)

## 1. Database (optional — SQLite works)
docker run --name evalai-postgres -e POSTGRES_DB=evalai -e POSTGRES_USER=evalai_user -e POSTGRES_PASSWORD=change_me_locally -p 5432:5432 -d postgres:16

## 2. Backend (D:\evalai\backend)
. .venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
# http://localhost:8000  (/docs + /health)

## 3. Frontend (D:\evalai\frontend)
cd ../frontend
npm install  (done)
npm run dev    # -> http://localhost:3001

## 4. Verify
Browser: http://localhost:3001/dashboard
API: curl http://localhost:8000/health

## 5. Do NOT commit .env
backend/.env has your GEMINI_API_KEY (already set, not committed).
