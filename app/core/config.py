import os
from dotenv import load_dotenv
load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "CPCG Tech Studio")
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "change-me")

    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://127.0.0.1:8000/auth/google/callback")
    
    # --- Mistral AI ---
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_OCR_MODEL: str = os.getenv("MISTRAL_OCR_MODEL", "mistral-ocr-2512")
    MISTRAL_CHAT_MODEL: str = os.getenv("MISTRAL_CHAT_MODEL", "mistral-small-latest")

    # --- Postgres ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
settings = Settings()
