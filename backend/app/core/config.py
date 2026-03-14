from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # JWT
    JWT_SECRET: str = "voxia-super-secret-key-cambia-esto-en-produccion"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Rate Limiting
    RATE_LIMIT_MAX_ATTEMPTS: int = 5
    RATE_LIMIT_WINDOW_SECONDS: int = 300

    # Modelos IA
    WHISPER_MODEL: str = "base"
    FLAN_T5_MODEL: str = "google/flan-t5-base"

    # Archivos
    MAX_FILE_SIZE_MB: int = 100
    UPLOAD_DIR: str = "uploads"
    TEMP_DIR: str = "temp"

    # Usuario admin por defecto
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "password123"
    ADMIN_DISPLAY_NAME: str = "Administrador VoxIA"

    class Config:
        env_file = ".env"


settings = Settings()
