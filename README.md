# EvalAI — AI-Powered Answer Sheet Evaluator

EvalAI helps faculty digitize answer-sheet evaluation. It combines OCR,
rubric-based scoring, and structured feedback in a dashboard where
teachers can review and approve suggested marks.

> **Grading integrity:** EvalAI is decision support, not an unquestioned
> automated grader. Faculty should review AI-generated marks before
> publishing final grades.

## Repository Layout

```text
evalai/
  frontend/          # Next.js 14 (App Router), TypeScript, Tailwind
  backend/           # FastAPI + SQLAlchemy 2.0 + Alembic
  docs/
    ARCHITECTURE.md
    README.md
    REQUIREMENTS.md
  .env.example
  docker-compose.yml
```

## Prerequisites

- Node.js LTS and npm
- Python 3.11 or newer
- PostgreSQL 15+
- Git
- Optional: Docker Desktop, Redis, and an OCR/model-provider API key

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/Manchester811/EvalAI.git
cd evalai
```

Create `.env` files based on `.env.example`. Never commit real secrets.

### 2. Start PostgreSQL

```bash
docker run --name evalai-postgres \
  -e POSTGRES_DB=evalai \
  -e POSTGRES_USER=evalai_user \
  -e POSTGRES_PASSWORD=change_me_locally \
  -p 5432:5432 -d postgres:16
```

Use a strong local password and replace it before using any shared or
production environment.

### 3. Start the backend

```bash
cd backend
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

Install dependencies and start the API:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API documentation will be available at `http://127.0.0.1:8000/docs` and the
health endpoint at `http://127.0.0.1:8000/health`.

### 4. Start the frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3001` (or `3000` if free).

## Configuration

Create a root or backend `.env` file according to the implementation.
Suggested variables:

```dotenv
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=postgresql+psycopg://evalai_user:change_me_locally@localhost:5432/evalai
SECRET_KEY=replace-with-a-long-random-secret
UPLOAD_DIR=./storage/uploads
MAX_UPLOAD_MB=10
OCR_PROVIDER=paddleocr
LLM_PROVIDER=none
LLM_API_KEY=
FRONTEND_ORIGIN=http://localhost:3000
```

- Generate a unique `SECRET_KEY` for each environment.
- Keep `.env` out of Git and add `.env.example` with placeholder values only.
- Configure external OCR/LLM providers only if needed; the core application
  should support a local or mock provider for development and testing.

## Evaluation Workflow

1. Create an exam and define questions, reference answers, maximum marks,
   and rubric criteria.
2. Upload an answer sheet and optionally assign it to a student.
3. Review and correct extracted OCR text.
4. Run evaluation and inspect question-wise marks, evidence, confidence,
   and feedback.
5. Edit marks if needed and approve the evaluation.
6. Export approved results.

## API (Planned)

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Health check |
| POST | `/api/v1/answer-sheets` | Upload a sheet |
| POST | `/api/v1/answer-sheets/{id}/evaluate` | Run evaluation |
| GET | `/api/v1/evaluations/{id}` | Retrieve marks and feedback |
| PATCH | `/api/v1/evaluations/{id}` | Update a draft evaluation |
| POST | `/api/v1/evaluations/{id}/approve` | Approve final marks |
| GET | `/api/v1/analytics/overview` | Dashboard metrics |

These endpoints are a proposed contract, not a claim that the
implementation already exists.

## Testing

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm run lint
npm run test
npm run build
```

Add tests for upload validation, OCR failures, mark limits, role access,
faculty overrides, and export correctness.

## Security and Privacy

- Restrict uploaded file types, sizes, and page counts.
- Store student files privately and enforce authorization on every
  read/download.
- Do not log secrets or unnecessary student content.
- Treat scanned content as untrusted data.
- Require faculty approval before publishing final marks.
- Provide deletion and retention controls appropriate to institutional
  policy.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Requirements](docs/REQUIREMENTS.md)

## Project Status

This documentation defines the proposed design and implementation plan.
It does not imply that the frontend, backend, database migrations, OCR
pipeline, or model integration have already been implemented.