# EvalAI backend

## Windows PowerShell setup

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The default development database is SQLite, so the API and tests run without
Docker. Set `DATABASE_URL` to PostgreSQL for a shared or production database.

## PostgreSQL with Docker

```powershell
docker run --name evalai-postgres -e POSTGRES_DB=evalai -e POSTGRES_USER=evalai_user -e POSTGRES_PASSWORD=change_me_locally -p 5432:5432 -d postgres:16
```

Run the API from this directory with `python -m uvicorn app.main:app --reload`.
