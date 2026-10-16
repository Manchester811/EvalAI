# EvalAI — Required Vercel + Backend Environment Variables

DO NOT put real secrets in this file. This is documentation, not a secret store.

## Vercel (Frontend — NEXT_PUBLIC_* only — never secrets)

| Variable | Required | Example / Notes |
|---|---|---|
| NEXT_PUBLIC_API_URL | YES | Set to your deployed backend URL when available. Example: `https://evalai-api.example.com`. Not invented — must be set after backend deploy. Local dev uses `http://localhost:8000` via `.env.local`. |

## Backend (`.env` — NOT committed; in `.gitignore`)

| Variable | Required | Notes |
|---|---|---|
| DATABASE_URL | YES | `postgresql+psycopg://...` for production; SQLite allowed for dev |
| SECRET_KEY | YES | Must be long random; production startup blocked if placeholder |
| GEMINI_API_KEY | NO | Only if using `OCR_PROVIDER=gemini` |
| OPENAI_API_KEY | NO | Only if using `OCR_PROVIDER=chatgpt` |
| FRONTEND_ORIGIN | YES | `http://localhost:3000`, `http://localhost:3001`, or deployed frontend URL |

## Do NOT expose in NEXT_PUBLIC_

- `SECRET_KEY`
- `DATABASE_URL`
- `LLM_API_KEY` / `GEMINI_API_KEY` / `OPENAI_API_KEY`
- `UPLOAD_DIR` paths

The backend `.env` is kept out of Git; `.env.local` only sets `NEXT_PUBLIC_API_URL` (public by design).
