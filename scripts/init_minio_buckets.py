"""Initialize MinIO buckets."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.utils.minio_client import ensure_buckets


def main():
    try:
        ensure_buckets()
        print("MinIO buckets initialized successfully.")
    except Exception as e:
        print(f"Warning: Could not initialize MinIO buckets: {e}")
        print("Make sure MinIO is running.")


if __name__ == "__main__":
    main()
