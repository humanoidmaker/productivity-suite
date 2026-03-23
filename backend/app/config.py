from __future__ import annotations
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "Productivity Suite"
    debug: bool = False
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Database
    database_url: str = "postgresql+asyncpg://productivity:productivity@localhost:5432/productivity"
    database_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: str = "change-me-in-production-use-a-long-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    minio_bucket_assets: str = "productivity-assets"
    minio_bucket_exports: str = "productivity-exports"
    minio_bucket_snapshots: str = "productivity-snapshots"
    minio_bucket_thumbnails: str = "productivity-thumbnails"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Quotas & Limits
    default_storage_quota_mb: int = 500
    max_file_size_mb: int = 50
    max_collaborators_per_file: int = 20
    auto_save_interval_seconds: int = 30
    version_snapshot_interval_minutes: int = 5
    max_versions_per_file: int = 50
    trash_auto_purge_days: int = 30

    # Rate limiting
    rate_limit_per_minute: int = 120

    # Registration
    registration_enabled: bool = True

    model_config = {"env_prefix": "WORKHUB_", "env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
