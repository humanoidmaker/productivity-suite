from __future__ import annotations
import io
from datetime import timedelta

from minio import Minio

from app.config import get_settings

settings = get_settings()

_client: Minio | None = None


def get_minio_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
    return _client


def ensure_buckets() -> None:
    """Create required buckets if they don't exist."""
    client = get_minio_client()
    buckets = [
        settings.minio_bucket_assets,
        settings.minio_bucket_exports,
        settings.minio_bucket_snapshots,
        settings.minio_bucket_thumbnails,
    ]
    for bucket in buckets:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)


def upload_bytes(bucket: str, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    """Upload bytes to MinIO and return the key."""
    client = get_minio_client()
    client.put_object(
        bucket_name=bucket,
        object_name=key,
        data=io.BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    return key


def download_bytes(bucket: str, key: str) -> bytes:
    """Download an object from MinIO and return its bytes."""
    client = get_minio_client()
    response = client.get_object(bucket, key)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def get_presigned_url(bucket: str, key: str, expires_hours: int = 1) -> str:
    """Generate a presigned download URL."""
    client = get_minio_client()
    return client.presigned_get_object(bucket, key, expires=timedelta(hours=expires_hours))


def delete_object(bucket: str, key: str) -> None:
    """Delete an object from MinIO."""
    client = get_minio_client()
    client.remove_object(bucket, key)
