# ByKP: Configuración Centralizada (Pydantic Settings)
# app/config.py
# Célula 04 - Asistente Virtual SIS-UNETI

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional
import os

class Settings(BaseSettings):
    # --- Información del Proyecto ---
    PROJECT_NAME: str = "Asistente Virtual SIS-UNETI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # --- Base de Datos (PostgreSQL) ---
    # Formato: postgresql://user:password@host:port/dbname
    DATABASE_URL: str = "postgresql://admin_uneti:superpassword2026@localhost:5433/asistente_virtual"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str) -> str:
        # Si corre dentro de Docker (señalado por IS_DOCKER=true en docker-compose)
        # Adaptamos localhost:5433 (externo) a postgres_db:5432 (interno)
        if os.getenv("IS_DOCKER") == "true":
            return v.replace("localhost:5433", "postgres_db:5432").replace("127.0.0.1:5433", "postgres_db:5432")
        return v

    # --- Caché (Redis) ---
    REDIS_URL: str = "redis://localhost:6379/0"

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_url(cls, v: str) -> str:
        if os.getenv("IS_DOCKER") == "true":
            return v.replace("localhost", "redis_cache").replace("127.0.0.1", "redis_cache")
        return v

    # --- Inteligencia Artificial (LLM API) ---
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-3.5-turbo" # Default
    LLM_BASE_URL: Optional[str] = None # Para proveedores compatibles con OpenAI

    # --- Seguridad ---
    SECRET_KEY: str = "cambiame_en_produccion_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 semana

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()
