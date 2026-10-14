from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    APP_ENV: str = "development"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    # SQLite keeps a fresh checkout runnable without requiring Docker. Set
    # DATABASE_URL to PostgreSQL in production or when using the compose setup.
    DATABASE_URL: str = "sqlite:///./evalai.db"
    SECRET_KEY: str = "replace-with-long-random-secret"
    UPLOAD_DIR: str = "./storage/uploads"
    MAX_UPLOAD_MB: int = 10
    OCR_PROVIDER: str = "paddleocr"
    LLM_PROVIDER: str = "none"
    LLM_API_KEY: str = ""
    EVALUATION_PROVIDER: str = "mock"
    FRONTEND_ORIGIN: str = "http://localhost:3000"

settings = Settings()


