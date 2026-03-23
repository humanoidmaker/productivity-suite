from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    total_users: int
    active_users: int
    total_documents: int
    total_spreadsheets: int
    total_presentations: int
    total_storage_bytes: int
    active_collaborations: int


class SystemHealth(BaseModel):
    postgres: bool
    redis: bool
    minio: bool
    celery_workers: int
    websocket_connections: int
    active_sessions: int


class SystemSettings(BaseModel):
    default_storage_quota_mb: int = Field(ge=1)
    max_file_size_mb: int = Field(ge=1)
    max_collaborators_per_file: int = Field(ge=1)
    auto_save_interval_seconds: int = Field(ge=5)
    version_snapshot_interval_minutes: int = Field(ge=1)
    max_versions_per_file: int = Field(ge=1)
    trash_auto_purge_days: int = Field(ge=1)
    registration_enabled: bool
    rate_limit_per_minute: int = Field(ge=10)
