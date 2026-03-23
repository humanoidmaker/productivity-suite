"""Tests for file utilities."""
from app.utils.file_utils import (
    generate_storage_key, generate_share_token, is_valid_image_type,
    get_file_extension, validate_file_size, sanitize_filename,
)


def test_storage_key_has_prefix():
    key = generate_storage_key("assets", "photo.jpg")
    assert key.startswith("assets/")
    assert key.endswith("photo.jpg")

def test_storage_key_unique():
    k1 = generate_storage_key("a", "b.txt")
    k2 = generate_storage_key("a", "b.txt")
    assert k1 != k2

def test_share_token_length():
    token = generate_share_token()
    assert len(token) > 20

def test_valid_image_type():
    assert is_valid_image_type("image/jpeg")
    assert is_valid_image_type("image/png")
    assert not is_valid_image_type("application/pdf")

def test_file_extension():
    assert get_file_extension("doc.docx") == ".docx"
    assert get_file_extension("no_ext") == ""

def test_validate_file_size():
    assert validate_file_size(1024, 1)  # 1KB < 1MB
    assert not validate_file_size(2 * 1024 * 1024, 1)  # 2MB > 1MB

def test_sanitize_filename():
    assert sanitize_filename("../../etc/passwd") == "passwd"
    assert sanitize_filename("normal.txt") == "normal.txt"
    assert sanitize_filename("has\x00null.txt") == "hasnull.txt"
