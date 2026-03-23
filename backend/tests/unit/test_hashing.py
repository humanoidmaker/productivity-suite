"""Tests for password hashing."""
from app.utils.hashing import hash_password, verify_password


def test_hash_returns_string():
    h = hash_password("secret123")
    assert isinstance(h, str)
    assert h != "secret123"

def test_verify_correct():
    h = hash_password("mypassword")
    assert verify_password("mypassword", h) is True

def test_verify_wrong():
    h = hash_password("mypassword")
    assert verify_password("wrong", h) is False

def test_different_hashes():
    h1 = hash_password("same")
    h2 = hash_password("same")
    assert h1 != h2  # bcrypt uses random salt

def test_hash_not_empty():
    assert len(hash_password("x")) > 20
