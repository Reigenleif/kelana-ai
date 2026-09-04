from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate .env file: first check root directory, then backend directory
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

ENV_FILE = ROOT_DIR / ".env" if (ROOT_DIR / ".env").exists() else BASE_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "Kelana AI API"
    app_version: str = "2.0.0"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/kelana_ai"

    # Security / JWT
    jwt_secret_key: str = "kelana-ai-super-secret-jwt-key-2026-secure"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # AWS Bedrock & Knowledge Base
    aws_region: str = "ap-southeast-2"
    model_id: str = "amazon.nova-lite-v1:0"
    knowledge_base_id: str = ""
    knowledge_base_s3_bucket: str = "kelana-s3-127490464453-ap-southeast-2-an"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_session_token: str | None = None

    # CORS
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
