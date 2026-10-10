import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "Health Insurance Intelligence Platform"
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    DATABASE_URL: str = "sqlite:///./health_insurance.db"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # RAG Pipeline Configuration
    EMBEDDING_PROVIDER: str = "local"  # "local", "sentence-transformers", "openai"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    VECTOR_STORE_PATH: str = "./vector_index.json"

    LLM_PROVIDER: str = "auto"  # "auto", "openai", "gemini", "ollama", "fallback"
    LLM_MODEL_NAME: str = "gpt-4o-mini"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    RAG_HYBRID_ALPHA: float = 0.5  # Weight for BM25 keyword vs Vector semantic scores
    RAG_MAX_CITATIONS: int = 5

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        if not self.CORS_ORIGINS:
            return ["http://localhost:5173", "http://127.0.0.1:5173"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
