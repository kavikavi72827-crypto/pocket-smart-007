import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    app_name = os.getenv("APP_NAME", "PocketSmart AI")
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    secret_key = os.getenv("SECRET_KEY", "PocketSmart-AI-Local-Development-Secret-2026")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    database_url = os.getenv("DATABASE_URL", str(BASE_DIR / "pocketsmart.db"))

settings = Settings()
