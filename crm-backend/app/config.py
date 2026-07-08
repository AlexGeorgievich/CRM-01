from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "CRM-MiniSystem"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    SECRET_KEY: SecretStr = Field(
        default="dev-secret-key-change-before-production-0001",
        min_length=32,
    )

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://crm_user:crm_password@postgres:5432/crm_db"
    SQL_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Auth
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # Initial data
    INITIAL_ADMIN_USERNAME: str = "admin"
    INITIAL_ADMIN_PASSWORD: SecretStr = Field(default="admin12345", min_length=8)
    INITIAL_ADMIN_FULL_NAME: str = "CRM Administrator"
    INITIAL_ADMIN_EMAIL: str | None = "admin@example.local"


settings = AppSettings()
